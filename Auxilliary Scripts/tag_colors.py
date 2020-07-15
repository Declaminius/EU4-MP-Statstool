#todo

country_color = compile("country_color=[{]\n\t\t\t\t(?P<color>[^\n]+).+?", DOTALL)
result = country_color.search(info)
if result:
    stats = {"country": tag}
    stats.update(result.groupdict())
    color = stats["color"].split()
    for i, n in zip(color, range(len(color))):
        color[n] = int(i)
    hex_color = ("#{0:02x}{1:02x}{2:02x}".format(*color))
    color_dict[stats["country"]] = hex_color
