import os
from dotenv import load_dotenv
from datetime import datetime

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import SitemapLoader, SeleniumURLLoader
from bs4 import BeautifulSoup
import requests

load_dotenv()

# Initialize embeddings and vector store
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory=os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_langchain_db"),
)

def get_all_urls(base_url: str) -> list:
    """Get URLs from sitemap and fallback to scraping"""
    urls = []

    # Try sitemap first
    try:
        sitemap_url = f"{base_url}/sitemap.xml"
        loader = SitemapLoader(sitemap_url)
        docs = loader.load()
        urls.extend([doc.metadata['source'] for doc in docs])
        print(f"Loaded {len(urls)} URLs from sitemap")
    except Exception as e:
        print(f"Sitemap loading failed: {e}")

    # Fallback to scraping homepage
    if not urls:
        try:
            response = requests.get(base_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and href.startswith(('http://', 'https://')):
                    if base_url in href:
                        urls.append(href)
                elif href and href.startswith('/'):
                    urls.append(f"{base_url.rstrip('/')}{href}")
            print(f"Loaded {len(urls)} URLs from homepage scraping")
        except Exception as e:
            print(f"Scraping failed: {e}")

    return list(set(urls))

def build_index():
    # Build index for both docs.atlan.com and developer.atlan.com
    base_urls = [
        "https://docs.atlan.com",
        "https://developer.atlan.com"
    ]
    
    all_docs = []
    
    for base_url in base_urls:
        print(f"\n=== Building index for {base_url} ===")
        urls = get_all_urls(base_url)

        if not urls:
            print(f"No URLs found for {base_url}")
            continue

        # Load content from URLs
        loader = SeleniumURLLoader(urls=urls)
        docs = loader.load()
        print(f"Loaded {len(docs)} documents from {len(urls)} URLs")

        # Add source and last_updated metadata
        for doc in docs:
            doc.metadata["last_updated"] = datetime.utcnow().isoformat()
            doc.metadata["source_site"] = base_url

        all_docs.extend(docs)

    if not all_docs:
        raise Exception("No documents found to load from any source")

    print(f"\nTotal documents loaded: {len(all_docs)}")

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_splits = text_splitter.split_documents(all_docs)
    print(f"Split into {len(all_splits)} chunks")

    # Avoid re-indexing existing sources
    existing = vector_store.get(include=["metadatas"])
    existing_sources = {m["source"] for m in existing["metadatas"] if "source" in m}
    new_splits = [d for d in all_splits if d.metadata.get("source") not in existing_sources]

    if new_splits:
        _ = vector_store.add_documents(documents=new_splits)
        print(f"Indexed {len(new_splits)} new/updated chunks")
    else:
        print("No new documents to index (all up-to-date)")

if __name__ == "__main__":
    build_index()
