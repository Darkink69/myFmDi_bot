from .telegram import webhook_handler

async def handler(request):
    return await webhook_handler(request)