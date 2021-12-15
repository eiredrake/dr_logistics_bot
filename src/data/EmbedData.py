import discord


class FieldObject(object):
    def __init__(self, name: str, value: str, inline: bool):
        self.name = name
        self.value = value
        self.inline = inline


class EmbedData(object):
    def __init__(self, title: str = None, description: str = None, color: discord.Color = discord.Color.darker_grey()):
        self.title = title
        self.description = description
        self.color = color
        self.parent_Id = None
        self.fields = dict()
        self.thumbnail = None
        self.image = None

    def add_field(self, name: str, value: str, inline: bool = False):
        field = FieldObject(name, value, inline)
        self.fields[field.name] = field

    def to_embed(self, parent_id: int = None):
        self.parent_Id = parent_id
        embed = discord.Embed(title=self.title, description=self.description, color=self.color)

        if self.parent_Id is not None:
            embed.set_footer(text='msg id: %s' % self.parent_Id)

        for field in self.fields:
            field_object = self.fields[field]
            if field_object.value is not None:
                embed.add_field(name=field, value=field_object.value)

        if self.thumbnail is not None:
            embed.set_thumbnail(url=self.thumbnail)

        if self.image is not None:
            embed.set_image(url=self.image)

        return embed

    @staticmethod
    def copy_embed(embed: discord.Embed, title: str = None, description: str = None, color: discord.Color = discord.Color.default()):
        if embed is None:
            raise ValueError("Embed is None")

        if title is None:
            title = embed.title

        if description is None:
            description = embed.description

        if color is None:
            color = embed.color

        result = discord.Embed(title=title, description=description, color=color)

        if len(embed.footer) > 0:
            result.set_footer(text=embed.footer.text)

        if len(embed.thumbnail) > 0:
            result.set_thumbnail(url=embed.thumbnail)

        if len(embed.image) > 0:
            result.set_image(url=embed.image)

        for field in embed.fields:
            result.add_field(name=field.name, value=field.value)

        return result

    @staticmethod
    def field_exists_by_name(embed: discord.Embed, field_name: str):
        if embed is None:
            raise ValueError("Embed is None")

        if field_name is None:
            raise ValueError("Field name is None")

        for field in embed.fields:
            if field.name == field_name:
                return True

        return False

    @staticmethod
    def get_field_value_by_name(embed: discord.Embed, field_name: str):
        if embed is None:
            raise ValueError("Embed is None")

        if field_name is None:
            raise ValueError("Field name is None")

        for field in embed.fields:
            if field.name == field_name:
                return field.value

        raise KeyError('No field name \'%s\' exists in the field list' % field_name)

    @staticmethod
    def get_field_by_name(embed: discord.Embed, field_name: str):
        if embed is None:
            raise ValueError("Embed is None")

        if field_name is None:
            raise ValueError("Field name is None")

        for field in embed.fields:
            if field.name == field_name:
                return field

        raise KeyError('No field name \'%s\' exists in the field list' % field_name)