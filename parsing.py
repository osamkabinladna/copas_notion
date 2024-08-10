import uuid
import re
from utils import clean_latex, link2id
from notion_client import Client as OfficialClient
import os

normalny_token = os.getenv('NOTION_KEY')


def generate_block_id():
    return str(uuid.uuid4())


def create_text_block(content):
    if content.strip() == "":
        return []
    return [{
        'object': 'block',
        'id': generate_block_id(),
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{
                'type': 'text',
                'text': {
                    'content': clean_latex(content),
                    'link': None
                },
                'annotations': {
                    'bold': False,
                    'italic': False,
                    'strikethrough': False,
                    'underline': False,
                    'code': False,
                    'color': 'default'
                },
                'plain_text': clean_latex(content),
                'href': None
            }],
            'color': 'default'
        }
    }]


def create_equation_inline(expression):
    return {
        'type': 'equation',
        'equation': {
            'expression': clean_latex(expression)
        },
        'annotations': {
            'bold': False,
            'italic': False,
            'strikethrough': False,
            'underline': False,
            'code': False,
            'color': 'default'
        },
        'plain_text': clean_latex(expression),
        'href': None
    }


def create_equation_block(expression):
    return {
        'object': 'block',
        'id': generate_block_id(),
        'type': 'equation',
        'equation': {
            'expression': clean_latex(expression)
        }
    }


def parse_to_notion_blocks(text):
    blocks = []
    square_re = r'\\\[(.*?)\\\]'
    parentheses_re = r'\\\((.*?)\\\)'

    # Split the string into paragraphs
    paragraphs = text.strip().split('\n\n')

    for paragraph in paragraphs:
        # Handle block equations
        if re.fullmatch(square_re, paragraph.strip()):
            blocks.append(create_equation_block(re.search(square_re, paragraph.strip()).group(1)))
        else:
            # Handle inline equations within paragraphs
            parts = re.split(r'(\\\(.+?\\\))', paragraph)
            paragraph_block = {
                'object': 'block',
                'id': generate_block_id(),
                'type': 'paragraph',
                'paragraph': {
                    'rich_text': [],
                    'color': 'default'
                }
            }

            for part in parts:
                if re.fullmatch(parentheses_re, part):
                    paragraph_block['paragraph']['rich_text'].append(create_equation_inline(re.search(parentheses_re, part).group(1)))
                else:
                    paragraph_block['paragraph']['rich_text'].append({
                        'type': 'text',
                        'text': {
                            'content': clean_latex(part),
                            'link': None
                        },
                        'annotations': {
                            'bold': False,
                            'italic': False,
                            'strikethrough': False,
                            'underline': False,
                            'code': False,
                            'color': 'default'
                        },
                        'plain_text': clean_latex(part),
                        'href': None
                    })

            blocks.append(paragraph_block)

    return {
        'object': 'list',
        'results': blocks,
        'next_cursor': None,
        'has_more': False,
        'type': 'block',
        'block': {},
        'request_id': generate_block_id()
    }


def append_blocks_to_notion_page(page_id, blocks):
    client = OfficialClient(auth=normalny_token)
    for block in blocks['results']:
        if block['type'] == 'paragraph':
            # If the block is a paragraph, make sure the rich_text is correctly structured
            rich_text = block['paragraph']['rich_text']
            client.blocks.children.append(block_id=page_id, children=[
                {
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': rich_text,
                        'color': block['paragraph']['color']
                    }
                }
            ])
        else:
            # For other block types like equations
            client.blocks.children.append(block_id=page_id, children=[block])

