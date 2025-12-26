from fastapi import APIRouter
from v13.atlas.src import build_info

router = APIRouter(prefix="/api/meta", tags=["Meta"])


@router.get("/build")
async def get_build_info():
    """
    Returns the deterministic build identity of the running service.
    Used by EvidenceBus and Electron UI for provenance.
    """
    return {
        "service": build_info.SERVICE_NAME,
        "version_tag": build_info.VERSION_TAG,
        "git_commit": build_info.GIT_COMMIT,
        "artifact_sha256": build_info.ARTIFACT_SHA256,
        "build_manifest_sha256": build_info.BUILD_MANIFEST_SHA256,
        "manifest": build_info.BUILD_MANIFEST,
    }
