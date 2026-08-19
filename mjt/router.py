from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status
from mjt.client import mjt_client

router = APIRouter(
    prefix="/api/mjt",
    tags=["MJT"],
)


@router.get(
    "/json_getInitialBuses",
    summary="Get Active Buses",
    description=(
        "Fetches active bus locations, headings, speed, operational status, and line associations "
        "from the upstream MJT system."
    ),
    responses={
        200: {
            "description": "Active buses payload with GPS coordinates and telemetry",
            "content": {
                "application/json": {
                    "example": {
                        "status": 1,
                        "message": "Success",
                        "data": [
                            {
                                "acc": "1",
                                "ago": "98",
                                "battery_percent": "1",
                                "company_nm": "Teman Bus",
                                "direction": "344",
                                "dist_shel": None,
                                "fleet_id": None,
                                "gap": "26",
                                "gps_sn": "869066064765085",
                                "gps_time": "2026-08-19 10:41:24",
                                "group_nm": "BTS",
                                "id": "869066064765085",
                                "ip": "114.122.68.242",
                                "jenroute": "BTS",
                                "kor": "FD-1",
                                "lat": -6.919581,
                                "lon": 107.609893,
                                "name": "FD-1 04",
                                "new_shel_t": "0041515",
                                "nopol": "D 1969 BD",
                                "old_shel_t": "0041703",
                                "port": "10351",
                                "pref": "63",
                                "prosen": None,
                                "protocol": "GT06-A0",
                                "route_id": "778",
                                "speed": 14,
                                "stime": "2026-08-19 10:41:24",
                                "toward": "Simpang Soetta Kiaracondong 2",
                            }
                        ],
                    }
                }
            },
        },
        502: {
            "description": "Failed to communicate with upstream MJT server",
            "content": {
                "application/json": {
                    "example": {"message": "Failed to fetch buses data: Upstream error"}
                }
            },
        },
    },
)
async def get_initial_buses() -> Dict[str, Any]:
    try:
        data = await mjt_client.get_initial_buses()
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch buses data: {str(e)}",
        )


@router.get(
    "/json_getRoutes",
    summary="Get Bus Routes",
    description=(
        "Fetches bus route geometries, coordinate waypoints, stop sequences, and route metadata "
        "from the upstream MJT system."
    ),
    responses={
        200: {
            "description": "Bus routes list with shelter points and encoded polyline path offsets",
            "content": {
                "application/json": {
                    "example": {
                        "status": 1,
                        "message": "Success",
                        "data": [
                            {
                                "id": "2122",
                                "route_id": "778",
                                "kor": "FD-1",
                                "color": "#22b473",
                                "points": "nrki@gr~oSNnAP`AfCjLdBtI~@bEtBtJaEbEgAdAuHhH}KnKHH]\\\\]IIcC|BW@_A_As@e@_DSk@IkBc@}D_AqAa@uAjDJBKCyBpF_@x@[^i@r@sBjBkAjAc@U}AgAu@i@i@YkCaA}@UkFiA_@pBUnAARG^Mb@]V_IoAuF}@M?MDOPeAjG_BpJyF_AcDk@WtA}By@mBo@K?IEEI?KeCi@UBoBg@SGWQ[GkEs@sAOi@@YDI?MLQD_E^uCViDT@PbA~B~DnJxDxIxAbDrBfFDREROLI@w@EuHc@yHWaCM?L?MmESsAOeC]e@Ac@HuGtCmAp@wFtCeDzAKaEM}C@wAf@aDl@wDUGSKQMOQMQMi@mHgAkB[[GqA[uAa@QSg@iAAOFcAEYKW_@k@eA{A}C}Dq@}@GCg@E_@Tk@FcGtBsAd@[TQTa@dA[rBW`AWp@u@jA]b@_CvCMRc@z@_@h@IHUPYJaAV@nAiB@kFDi@LA\\Bz@DbC@lAK`BQx@I`APl@b@l@nBhBpBfBlCmDpA`A`@\\Z^Z`@DNDjBFZjAvAb@h@VPlC|ARN`CvC`FjGbAhAdB?vB?L}Ed@VVDx@EbAMlD_A|Bu@r@YHi@\\cArAcD`@S`IwBn@|Bj@pBPNHBV@PClAc@dAo@vBgATGR?X?v@Fw@nJGpAUzE?^BVNNrERrDLjBwEj@sAr@?fBFpAHEb@KvAJ`APrDeDl@@FAGuGjAIDEFB\\E`BGVUh@IJo@j@w@h@CVGpACvBDn@PfAVjBXnCpERlBHfDJd@qB",
                                "route": "Simpang Soetta Kircon - Pasar Baru ABC",
                                "origin": "Simpang Soetta Kiaracondong 2",
                                "toward": "Pasar Baru ABC",
                                "jam_ops": "04:30 - 20:00",
                                "is_ops": "1",
                                "shelters": [
                                    {
                                        "latitude": -6.9475,
                                        "longitude": 107.635278,
                                        "nama_selter": "SPBU Simpang Buah Batu Soekarno Hatta",
                                        "kategori": "Shelter",
                                    }
                                ],
                                "points_offset": "prki@gr~oS?p@X`B`Kte@HXZv@BPKNcAx@wFtF_ShRQPCPQRA@@KBEHE?AKBKJcB~AMHO?MG{@w@k@_@uCSu@KwFqA}Bo@c@t@q@dB?DBBG@GJmBxEc@`AkAxAmBdB_A~@KFGA[OcBmAeAo@c@SkC_AwEeAy@MC?ABmAnGIJUJc@CcAWeMoBUAOJIR{CpQGZEDG@iFy@aDk@E?ABW~@CDE?{EcBWEIGGKEAqBc@]E]Ow@Sg@Gc@UyEw@sAOq@?c@FSLSDeIr@_DTMBAHFT~FfNtDpIzAbDrBdFDL?NEJQJQB{AIm@A{E]qHWwBKM?CDCEEAcESyEi@e@Ck@JeGlCmIjEuCrAMBCMIoDMuC@wABYbAsGFa@?M_@O_@WSYOe@GI{GaA{B_@oBe@mA_@W[c@cAAQDcAEWO]_B_CiEuFQMWEMBYNs@L_IpCUJYTQV]|@_@zBSx@]v@u@jAwCtDq@nA_@h@_@Z{@VYNAx@ELiILWBUHCLATDxB?bCK~AMbAIx@BVLThCfCdBxAVXd@e@~AwBFCH@b@VhAbAv@`AFXD`BDTJPhBvB|D~B^r@`IzJV`@XRNBhD?`@@DABMHyDBKD?\\NVDx@Cz@KtDaAjDkAHKFi@X{@nA}CJKZOxHqBD?FJtA~ENPJB\\@\\GdAq@p@_@nCoALCf@?f@DND@FAZs@rI_@|HANBNHJDB~Jb@FAHMnCyGNEX?vBJx@DJB@JMlBH`AP`DANMFuCj@iF|@u@TCH?f@CnAOd@MZIJo@j@o@b@EDGNCVErAFp@Ir@Dn@ZpBZlCBPRf@z@NxFV|CHFAFKZcB",
                            }
                        ],
                    }
                }
            },
        },
        502: {
            "description": "Failed to communicate with upstream MJT server",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Failed to fetch routes data: Upstream error"
                    }
                }
            },
        },
    },
)
async def get_routes() -> Dict[str, Any]:
    try:
        data = await mjt_client.get_routes()
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch routes data: {str(e)}",
        )


@router.get(
    "/token",
    summary="Get Session Tokens",
    description=(
        "Retrieves the active session tokens (`pis_nonce`, `mjt_cookie`, and `xtoken_cookie`).\n\n"
        "- **Cached**: Responses are served from an in-memory cache based on the upstream `pisNonceTtl` window.\n"
        "- **Force Refresh**: Pass query parameter `refresh=true` to force renewal from upstream immediately."
    ),
    responses={
        200: {
            "description": "Current active session token payload",
            "content": {
                "application/json": {
                    "example": {
                        "pis_nonce": "cjU4YmhxZ3A4NnZicm5nZGZiMTdndTNuNnQxazJpMmF8MTc4NzExMDI0MnxiYjI0ODNkZDU2YzczMGY5.2ecba2b0d1e73a360d1dc2a8f24ccb9df16eb060a737375eb52559ee91aea405",
                        "mjt_cookie": "r58bhqgp86vbrngdfb17gu3n6t1k2i2a",
                        "xtoken_cookie": "3ae3496b26bc166a755b0ca6123ee4c5",
                        "expires_in": 299,
                        "cached": True,
                    }
                }
            },
        },
        502: {
            "description": "Failed to communicate with upstream MJT server",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Failed to fetch tokens from MJT server: Connection timed out"
                    }
                }
            },
        },
    },
)
async def get_tokens(refresh: bool = False):
    try:
        tokens = await mjt_client.get_tokens(force=refresh)
        return tokens
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch tokens from MJT server: {str(e)}",
        )
