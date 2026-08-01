from __future__ import annotations

from pathlib import Path


def sync_directory(local_dir: str | Path, parent_folder_id: str) -> list[dict]:
    """Upload or update a local run directory using Google ADC credentials."""
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    service = build("drive", "v3")
    local_dir = Path(local_dir)
    results: list[dict] = []

    def ensure_folder(name: str, parent: str) -> str:
        escaped = name.replace("'", "\\'")
        query = (
            f"name='{escaped}' and '{parent}' in parents and "
            "mimeType='application/vnd.google-apps.folder' and trashed=false"
        )
        found = service.files().list(q=query, fields="files(id,name)").execute().get("files", [])
        if found:
            return found[0]["id"]
        body = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent],
        }
        return service.files().create(body=body, fields="id").execute()["id"]

    def upload_file(path: Path, parent: str) -> None:
        escaped = path.name.replace("'", "\\'")
        query = f"name='{escaped}' and '{parent}' in parents and trashed=false"
        found = service.files().list(q=query, fields="files(id,name)").execute().get("files", [])
        media = MediaFileUpload(str(path), resumable=True)
        if found:
            item = service.files().update(
                fileId=found[0]["id"], media_body=media, fields="id,name,md5Checksum"
            ).execute()
        else:
            item = service.files().create(
                body={"name": path.name, "parents": [parent]},
                media_body=media,
                fields="id,name,md5Checksum",
            ).execute()
        results.append(item)

    def walk(directory: Path, parent: str) -> None:
        for item in sorted(directory.iterdir()):
            if item.is_dir():
                walk(item, ensure_folder(item.name, parent))
            elif item.is_file():
                upload_file(item, parent)

    walk(local_dir, parent_folder_id)
    return results
