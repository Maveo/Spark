from typing import *

import discord.ui


class CustomButton(discord.ui.Button):
    def __init__(self,
                 callback: Callable[['CustomButton', discord.Interaction], Coroutine] = None,
                 data=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data
        self.custom_callback = callback

    async def callback(self, interaction: discord.Interaction):
        if self.custom_callback:
            await self.custom_callback(self, interaction)


class ViewPaginator:
    def __init__(self,
                 pages: List[discord.ui.View] = None,
                 hide_empty=False
                 ):
        if pages is None:
            pages = []
        self.pages = pages
        self.hide_empty = hide_empty
        self.current_page = 0
        self.prev_page_label = '️'
        self.prev_page_emoji = '⬅'
        self.prev_page_style = discord.ButtonStyle.secondary
        self.current_page_label = '{}/{}'
        self.current_page_style = discord.ButtonStyle.secondary
        self.next_page_label = ''
        self.next_page_emoji = '➡'
        self.next_page_style = discord.ButtonStyle.secondary

    def view(self):
        view = discord.ui.View()
        for child in self.pages[self.current_page].children:
            view.add_item(child)

        if len(self.pages) > 1 or not self.hide_empty:
            async def cb(button, interaction: discord.Interaction):
                self.current_page += button.data
                await interaction.response.edit_message(view=self.view())

            view.add_item(CustomButton(cb,
                                       data=-1,
                                       row=4,
                                       label=self.prev_page_label,
                                       emoji=self.prev_page_emoji,
                                       style=self.prev_page_style,
                                       disabled=self.current_page == 0))
            view.add_item(CustomButton(row=4,
                                       label=self.current_page_label.format(self.current_page + 1, len(self.pages)),
                                       style=self.current_page_style,
                                       disabled=True))
            view.add_item(CustomButton(cb,
                                       data=1,
                                       row=4,
                                       label=self.next_page_label,
                                       emoji=self.next_page_emoji,
                                       style=self.next_page_style,
                                       disabled=self.current_page == len(self.pages) - 1))
        return view
