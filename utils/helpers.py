async def send_message_in_chunks(channel, content, chunk_size=2000):
    for i in range(0, len(content), chunk_size):
        await channel.send(content[i:i + chunk_size])
