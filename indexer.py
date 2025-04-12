import faiss

import numpy as np
import json
import os
from embedder import get_embedding
from utils import load_json

class MultiDatasetIndexer:
    def __init__(self):
        self.datasets = {
            "stocks": {
                "path": "data/cleaned_stock_data.json",
                "index_path": "faiss_stocks.index",
                "metadata_path": "metadata_stocks.json"
            },
            "mutual_funds": {
                "path": "data/mutual_funds_cleaned.json",
                "index_path": "faiss_mf.index",
                "metadata_path": "metadata_mf.json"
            },
            "etfs": {
                "path": "data/mfh_cleaned.json",
                "index_path": "faiss_etf.index",
                "metadata_path": "metadata_etf.json"
            }
            
        }
        

        self.indices = {}
        self.metadatas = {}

    def build_index_for(self, key):
        config = self.datasets[key]
        funds = load_json(config["path"])
        embeddings = []
        metadata = []

        # Load MF scheme metadata if working with holdings (ETF)
        scheme_lookup = {}
        if key == "etfs":
            mf_path = self.datasets["mutual_funds"]["path"]
            mutual_funds = load_json(mf_path)
            scheme_lookup = {
                mf["schemeCode"]: mf for mf in mutual_funds if "schemeCode" in mf
            }

        for fund in funds:
            enriched = fund.copy()

            # Match schemeCode to enrich with scheme metadata
            if key == "etfs":
                scheme_code = fund.get("parentSchemeCode")
                if scheme_code in scheme_lookup:
                    mf_meta = scheme_lookup[scheme_code]
                    # Add key metadata fields to the holding
                    enriched["amcName"] = mf_meta.get("amcName")
                    enriched["schemeName"] = mf_meta.get("schemeName")
                    enriched["category"] = mf_meta.get("category")
                    enriched["subCategory"] = mf_meta.get("subCategory")
                    enriched["riskOMeter"] = mf_meta.get("riskOMeter")
                    enriched["assetType"] = mf_meta.get("assetType")

            # Build embedding from structured metadata fields only
            fields = [
                enriched.get("schemeName"),
                enriched.get("category"),
                enriched.get("subCategory"),
                enriched.get("fund_type"),
                enriched.get("sector"),
                enriched.get("industry"),
                enriched.get("amcName"),
                enriched.get("rating"),
                enriched.get("asset"),
                enriched.get("assetType"),
                enriched.get("investmentDate"),
                enriched.get("marketValue"),
                enriched.get("holdingPercentage"),
                enriched.get("aum")
            ]

            query_string = " ".join(str(val) for val in fields if val is not None)
            emb = get_embedding(query_string)
            embeddings.append(emb)
            metadata.append(enriched)

        embeddings = np.array(embeddings).astype("float32")
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)

        self.indices[key] = index
        self.metadatas[key] = metadata

        faiss.write_index(index, config["index_path"])
        with open(config["metadata_path"], "w", encoding="utf-8") as f:
            json.dump(metadata, f)
    def build_or_load_all(self):
        for key, config in self.datasets.items():
            if os.path.exists(config["index_path"]) and os.path.exists(config["metadata_path"]):
                self.indices[key] = faiss.read_index(config["index_path"])
                with open(config["metadata_path"], "r", encoding="utf-8") as f:
                    self.metadatas[key] = json.load(f)
            else:
                self.build_index_for(key)




