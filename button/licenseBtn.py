from discord.ui import Modal, TextInput
from discord import Interaction, TextStyle, Color, Embed
from function import DB

class registerModal(Modal, title='⏰ㅣ연장/등록하기'):
    licenseVar = TextInput(
        label='라이센스 키를 입력 해 주세요.',
        style=TextStyle.short,
        placeholder='1s3w5-1f3df-1cvbs-qwert',
        max_length=23,
        min_length=23
    )

    def __init__(self, instance):
        super().__init__()
        self.instance = instance

    async def on_submit(self, i: Interaction):  # interaction을 i로 변경
        registers = await DB.registerGuild(int(i.guild_id), str(self.licenseVar))  # interaction을 i로 변경
        if not registers:
            embed = Embed(title='라이센스 등록 실패',
                description='- 시도하신 라이센스를 확인 하시고 다시 이용 해 주시길 바랍니다.',
                color=Color.red())
            embed.set_footer(text=f"Zita Restore", icon_url=f"https://i.imgur.com/X2gz8W2.png")
            return await i.response.send_message(embed=embed, ephemeral=True)

        embed = Embed(
            title="라이센스 등록/연장 성공",
            description="- `/설정`을 통해 설정을 마무리 해 주세요.\n- `/인증`명령어를 통해 인증 임베드를 출력 가능합니다.",
            color=Color.green()
        )
        embed.set_footer(text=f"Zita Restore", icon_url=f"https://i.imgur.com/X2gz8W2.png")
        await i.response.send_message(embed=embed, ephemeral=True)
        await self.instance.btn(1)
        if registers != True:
            dm = await i.user.create_dm()  # interaction을 i로 변경
            embed1 = Embed(title="Restore Service", description=f">>> 복구키는 `{registers}`입니다.\n-# 이 키는 저장 하거나 기억 해두세요.", color=Color.green())
            embed1.set_footer(text="Zita Restore", icon_url="https://i.imgur.com/X2gz8W2.png")
            await dm.send(embed=embed1)

        # 응답이 완료되지 않은 경우에만 모달을 보냄
        if not i.response.is_done():
            return await i.response.send_modal(registerModal(self.instance))  # self.instance로 변경