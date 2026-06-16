#!/usr/bin/env python3
"""
Load ticket CSV datasets into the database and index them in ChromaDB.

Usage:
    Place CSV files in data/tickets/ then:
    cd backend
    python ../scripts/load_datasets.py

Supported: any CSV that has at least a title/description column.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from core.database import AsyncSessionFactory
from ingestion.ticket_loader import TicketLoader
from repositories.ticket_repo import TicketRepository
from services.ticket_service import TicketService


TICKETS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "tickets")


async def load():
    os.makedirs(TICKETS_DIR, exist_ok=True)
    csv_files = [f for f in os.listdir(TICKETS_DIR) if f.endswith(".csv")]
    
    total_inserted = 0
    total_skipped = 0

    async with AsyncSessionFactory() as db:
        repo = TicketRepository(db)
        
        if csv_files:
            loader = TicketLoader()
            for csv_file in csv_files:
                path = os.path.join(TICKETS_DIR, csv_file)
                print(f"\nProcessing: {csv_file}")
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    text = f.read()

                records = loader.parse_csv(text, source_dataset=csv_file)
                if not records:
                    print(f"  [WARNING] No records parsed from {csv_file}")
                    continue

                inserted = await repo.bulk_create(records)
                skipped = len(records) - inserted
                await db.commit()

                print(f"  [SUCCESS] Inserted: {inserted}, Skipped (duplicates): {skipped}")
                total_inserted += inserted
                total_skipped += skipped
        else:
            print("\nNo CSV files found. Loading 'mindweave/help-desk-tickets' from Hugging Face...")
            try:
                from datasets import load_dataset
                tickets = load_dataset("mindweave/help-desk-tickets", "tickets")["train"]
                categories = load_dataset("mindweave/help-desk-tickets", "categories")["train"]
            except Exception as e:
                print(f"  [ERROR] Failed to load dataset from Hugging Face: {e}")
                return

            cat_mapping = {row["id"]: row["name"] for row in categories}
            records = []
            seen_numbers = set()
            
            for i, row in enumerate(tickets):
                ticket_number = f"MW-T-{row['ticket_id']:06d}"
                if ticket_number in seen_numbers:
                    continue
                seen_numbers.add(ticket_number)
                
                category_name = cat_mapping.get(row["category_id"], "IT Support")
                
                priority = row["priority"].lower().strip()
                if priority in ("p1", "critical", "urgent"):
                    norm_priority = "critical"
                elif priority in ("p2", "high"):
                    norm_priority = "high"
                elif priority in ("p3", "medium", "moderate"):
                    norm_priority = "medium"
                elif priority in ("p4", "low"):
                    norm_priority = "low"
                else:
                    norm_priority = "medium"
                    
                status = row["status"].lower().strip()
                if status in ("open", "new"):
                    norm_status = "open"
                elif status in ("in progress", "in_progress", "pending"):
                    norm_status = "in_progress"
                elif status in ("resolved", "solved"):
                    norm_status = "resolved"
                elif status in ("closed", "done"):
                    norm_status = "closed"
                else:
                    norm_status = "open"

                records.append({
                    "ticket_number": ticket_number,
                    "title": row["summary"][:500],
                    "description": row["description"] or None,
                    "resolution": None,
                    "category": category_name,
                    "priority": norm_priority,
                    "status": norm_status,
                    "tags": [],
                    "source_dataset": "mindweave/help-desk-tickets",
                })
            
            inserted = await repo.bulk_create(records)
            skipped = len(records) - inserted
            await db.commit()
            
            print(f"  [SUCCESS] Inserted: {inserted}, Skipped (duplicates): {skipped}")
            total_inserted += inserted
            total_skipped += skipped

    print(f"\n{'='*50}")
    print(f"Total inserted: {total_inserted}")
    print(f"Total skipped:  {total_skipped}")
    print("\nNow run reindex to embed tickets into ChromaDB:")
    print("  POST /api/tickets/reindex")
    print("or use the Admin Dashboard -> Reindex button")


if __name__ == "__main__":
    asyncio.run(load())
