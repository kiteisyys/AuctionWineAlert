import discord

QUALITY_COLORS = {
    'legendary': discord.Color.gold(),
    'great': discord.Color.green(),
    'good': discord.Color.blue(),
    'average': discord.Color.light_grey(),
    'poor': discord.Color.red(),
    'unknown': discord.Color.greyple(),
}

QUALITY_EMOJI = {
    'legendary': '🏆',
    'great': '⭐',
    'good': '✅',
    'average': '➖',
    'poor': '⚠️',
    'unknown': '❓',
}

def make_embed(wine, vintage_quality, discount_pct, market_price, price_source):
    color = QUALITY_COLORS.get(vintage_quality, discord.Color.greyple())
    emoji = QUALITY_EMOJI.get(vintage_quality, '❓')

    embed = discord.Embed(
        title=wine['name'],
        url=wine['url'],
        color=color
    )

    embed.add_field(name="Category", value=wine['category'], inline=True)
    embed.add_field(name="Vintage", value=str(wine.get('vintage', 'N/A')), inline=True)
    embed.add_field(name="Vintage Quality", value=f"{emoji} {vintage_quality.capitalize()}", inline=True)

    embed.add_field(name="WineBid Price", value=f"${wine['price']:.2f}", inline=True)
    if market_price:
        embed.add_field(name="Market Price", value=f"${market_price:.2f}", inline=True)
        embed.add_field(name="Discount", value=f"{discount_pct}% off" if discount_pct else "N/A", inline=True)
        embed.add_field(name="Price Source", value=price_source, inline=False)
    else:
        embed.add_field(name="Market Price", value="No data found — flagged for review", inline=True)

    if wine.get('ratings'):
        embed.add_field(name="Critic Scores", value=wine['ratings'], inline=False)

    if wine.get('thumbnail'):
        embed.set_thumbnail(url=wine['thumbnail'])

    embed.set_footer(text="WineBid Auction Alert • Click the title above to view listing")

    return embed

async def send_wines(channel, results, scan_type="Scheduled"):
    if not results:
        await channel.send(f"**{scan_type} scan complete** — No wines matched your criteria.")
        return

    await channel.send(f"**{scan_type} scan complete — {len(results)} wine(s) found:**")
    for wine, vintage_quality, discount_pct, market_price, price_source in results:
        embed = make_embed(wine, vintage_quality, discount_pct, market_price, price_source)
        await channel.send(embed=embed)
