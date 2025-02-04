from discord import Interaction, Color, ButtonStyle
from discord.ui import Button, button, View
from function import DB
import discord

async def webhookCallback(instance, i: Interaction, btn: Button, data: list, webhook: list):
    if not data[4]:
        embed = discord.Embed(title=":warning: 연장/등록 필요", description="- 라이센스가 만료 되어있네요. 연장 해 주세요.", color=Color.red())
        return await i.response.send_message(embed=embed, ephemeral=True)

    class webhookBtn(View):
        def __init__(self, instance):
            super().__init__(timeout=None)
            self.instance = instance

        @button(label="이 체널에 웹훅설정하기", emoji="💬", style=ButtonStyle.green)
        async def thisChannelSetWebhook(self, i: Interaction, btn: Button):
            wbhook = await i.channel.create_webhook(name="Verify LOG")
            wbhook = wbhook.url
            await DB.set_webhook([wbhook, webhook[1]], i.guild_id)
            await msg.delete()
            await i.response.send_message(content="- 웹훅 설정을 완료 하였어요.", ephemeral=True)
            return await self.instance.btn(1)

        @button(label="다른 체널에 웹훅설정하기", emoji="💬", style=ButtonStyle.red, row=1)
        async def otherChannelSetWebhook(self, i: Interaction, btn: Button):
            wbhook = await i.channel.create_webhook(name="Verify LOG")
            class wbhookModal(discord.ui.Modal, title = "💬ㅣ웹훅설정"):
                wbhook = discord.ui.TextInput(
                    label="웹후크 URI를 적어주세요.",
                    style=discord.TextStyle.short,
                    placeholder="웹후크 URI"
                )

                def __init__(self, instance):
                    super().__init__()
                    self.instance = instance

                async def on_submit(self, interaction: Interaction):
                    wbhook = str(self.wbhook)
                    await DB.set_webhook([wbhook, webhook[1]], interaction.guild_id)
                    await msg.delete()
                    await interaction.response.send_message(content="- 웹훅 설정을 완료 하였어요.", ephemeral=True)
                    return await self.instance.btn(1)
            return await i.response.send_modal(wbhookModal(self.instance))
    await i.response.send_message(view=webhookBtn(instance), ephemeral=True)
    msg = await i.original_response()
    return