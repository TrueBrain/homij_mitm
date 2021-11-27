import aiohttp
import logging

from aiohttp import web

log = logging.getLogger(__name__)
routes = web.RouteTableDef()

HOMIJ_FORWARDER = None


@routes.post("/_ua/{identifier}/")
async def data_handler(request):
    # Get the required data from the request
    identifier = request.match_info["identifier"]
    basen_microagent_path = request.headers.get("BASEN-MICROAGENT-PATH")
    authorization = request.headers.get("AUTHORIZATION")
    host = request.headers.get("HOST")
    data = await request.read()

    HOMIJ_FORWARDER.rawfile_write(data, host)

    try:
        await HOMIJ_FORWARDER.process_request(data)
    except Exception:
        log.exception("process_request() failed")
        pass

    # Set headers that the scripts on the Raspberry Pi also set.
    headers = {}
    if basen_microagent_path:
        headers["basen-microagent-path"] = basen_microagent_path
    if authorization:
        headers["Authorization"] = authorization

    if HOMIJ_FORWARDER.dont_forward:
        content_type = "application/json"
        status = 200
        body = b'[{"duration":0,"data":"Wrote 1 rows","error":0,"info":"Wrote 1 rows"}]'
    else:
        # Create the call to the real webserver.
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://{host}/_ua/{identifier}/", data=data, headers=headers) as resp:
                content_type = resp.headers.get("CONTENT-TYPE").split(";")[0]
                status = resp.status
                body = await resp.read()

    # Respond with what-ever the real webserver was saying.
    # We do not pass along any headers, except content-type.
    return web.Response(status=status, body=body, content_type=content_type)


@routes.route("*", "/{tail:.*}")
async def fallback(request):
    log.error("Unexpected URL: %s", request.url)
    return web.Response()


def set_homij_forwarder(forwarder):
    global HOMIJ_FORWARDER
    HOMIJ_FORWARDER = forwarder
