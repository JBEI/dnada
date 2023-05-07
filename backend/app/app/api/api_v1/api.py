from fastapi import APIRouter

from app.api.api_v1.endpoints import (assemblys, banner, constructs,
                                      designs, digests, experiments,
                                      instructions, login, meta, oligos,
                                      parts, pcrs, runs, standalone,
                                      synths, users, utils, validate,
                                      workflow)

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(experiments.router, tags=["experiments"])
api_router.include_router(constructs.router, tags=["constructs"])
api_router.include_router(designs.router, tags=["designs"])
api_router.include_router(pcrs.router, tags=["pcrs"])
api_router.include_router(runs.router, tags=["runs"])
api_router.include_router(oligos.router, tags=["oligos"])
api_router.include_router(parts.router, tags=["parts"])
api_router.include_router(assemblys.router, tags=["assemblys"])
api_router.include_router(digests.router, tags=["digests"])
api_router.include_router(synths.router, tags=["synths"])
api_router.include_router(standalone.router, tags=["standalone"])
api_router.include_router(workflow.router, tags=["workflow"])
api_router.include_router(meta.router, tags=["meta"])
api_router.include_router(instructions.router, tags=["instructions"])
api_router.include_router(banner.router, tags=["banner"])
api_router.include_router(validate.router, tags=["validate"])
