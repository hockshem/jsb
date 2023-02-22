from typing import List
from discord.ext import commands
from membercard import create_membercard_embed

class JerSideBitch(commands.Bot):
    def __init__(
        self, 
        *args,
        initial_extensions: List[str],
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.initial_extensions = initial_extensions
    
    async def setup_hook(self) -> None:
        for extension in self.initial_extensions:
            await self.load_extension(extension)
    
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        await create_membercard_embed(self)