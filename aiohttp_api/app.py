from aiohttp import web
import json
import aiohttp_cors
import asyncio
import aiopg


dsn = 'dbname=aiopg user=oleg password=1987 host=127.0.0.1'
async def go():
    pool = await aiopg.create_pool(dsn)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT 1")
            ret = []
            async for row in cur:
                ret.append(row)
            assert ret == [(1,)]

loop = asyncio.get_event_loop()
loop.run_until_complete(go())


async def handle(request):
    test = request.query
    response_obj = { 'status' : 'success' }
    return web.Response(text=json.dumps(response_obj))


async def new_user(request):
    try:
        # happy path where name is set
        user = request.query['name']
        # Process our new user
        print("Creating new user with name: ", user)

        response_obj = {'status': 'success'}
        # return a success json response with status code 200 i.e. 'OK'
        return web.Response(text=json.dumps(response_obj), status=200)
    except Exception as e:
        # Bad path where name is not set
        response_obj = {'status': 'failed', 'reason': str(e)}
        # return failed with a status code of 500 i.e. 'Server Error'
        return web.Response(text=json.dumps(response_obj), status=500)

app = web.Application()

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
})

resource = cors.add(app.router.add_resource("/user"))
cors.add(resource.add_route("POST", new_user))
cors.add(resource.add_route("GET", new_user))

resource2 = cors.add(app.router.add_resource("/"))
cors.add(resource2.add_route("POST", handle))
cors.add(resource2.add_route("GET", handle))

# app.router.add_get('/', handle)
# app.router.add_post('/user', new_user)

web.run_app(app)