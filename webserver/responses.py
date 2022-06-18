from fastapi.responses import Response


class BytesFileResponse(Response):
    def __init__(self, content=bytes(), content_disposition='inline', filename=None, *args, **kwargs):
        if filename is not None:
            content_disposition = content_disposition + '; filename="{}"'.format(filename)
        headers = {
            'Content-Disposition': content_disposition,
        }
        if hasattr(content, 'read') and callable(content.read):
            content = content.read()
        if 'headers' in kwargs:
            headers = {**headers, **kwargs['headers']}
        super().__init__(
            *args,
            content=content,
            headers=headers,
            **kwargs,
        )
