from http.server import HTTPServer, BaseHTTPRequestHandler
import pdb
import typing


class Resopne:
    def __init__(self, status: int, body: str):
        self.status = status
        self.body_bytes = body.encode("utf8")


class Request:
    def __init__(
        self,
        command: str,
        client_address: typing.Tuple[str, int],
        path: str,
        server_version: str,
        sys_version: str,
        date_time_string: str,
        headers: typing.Dict[str, str],
        body_bytes: bytes,
    ):
        self.command = command
        self.client_address = client_address
        self.path = path
        self.server_version = server_version
        self.sys_version = sys_version
        self.date_time_string = date_time_string
        self.headers = headers
        self.body = body_bytes.decode("utf8")


def handle_info(request: Request):
    ans = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body>
    <p>command = {request.command}</p>
    <p>client_address = {request.client_address}</p>
    <p>path = {request.path}</p>
    <p>server_version = {request.server_version}</p>
    <p>sys_version = {request.sys_version}</p>
    <p>date_time_string = {request.date_time_string}</p>
    <p>request headers = {request.headers}</p>
</body>
</html>
    """
    return Resopne(200, ans)


def handle_square(request: Request):
    str_data = request.body
    try:
        n = int(str_data)
        ans = str(n ** 2)
        return Resopne(200, ans)
    except ValueError as ex:
        ans = str(ex)
        return Resopne(400, ans)


def handle_increment(request: Request):
    str_data = request.body
    try:
        n = int(str_data)
        ans = str(n + 1)
        return Resopne(200, ans)
    except ValueError as ex:
        ans = str(ex)
        return Resopne(400, ans)


def handle_increment_html(request: Request):
    ans = r"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Increment</title>
</head>
<body>
    <p>Click this button to increment a number:</p>
    <button type="button" onclick="changeNumber()">Change content</button>
    <p id="number">0</p>

    <script>
    let n = 0
    function changeNumber() {
      let xhttp = new XMLHttpRequest()
      xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
          let ajaxResult = parseInt(this.responseText)
          document.getElementById("number").innerHTML = ajaxResult
          n = ajaxResult
        }
      }
      xhttp.open("POST", "increment")
      xhttp.send(n)
    }
    </script>

</body>
</html>
    """
    return Resopne(200, ans)


handlers_map = {
    "/info": handle_info,
    "/square": handle_square,
    "/increment": handle_increment,
    "/increment.html": handle_increment_html,
}


class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.__handle_path()

    def do_POST(self):
        self.__handle_path()

    def __handle_path(self):
        if self.path not in handlers_map:
            self.send_error(404, f"Path Not Found: {self.path}")
            return
        else:
            CONTENT_LENGTH_HEADER = "Content-Length"
            content_length = 0
            if CONTENT_LENGTH_HEADER in self.headers:
                try:
                    content_length = int(self.headers[CONTENT_LENGTH_HEADER])
                except ValueError:
                    pass
            print(f"{content_length=}")
            req = Request(
                self.command,
                self.client_address,
                self.path,
                self.server_version,
                self.sys_version,
                self.date_time_string(),
                dict(self.headers.items()),
                self.rfile.read(content_length),
            )
            print(f"request body = '{req.body}'")
            handler = handlers_map[self.path]
            respons = handler(req)
            self.send_response(respons.status)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(respons.body_bytes)
            return


if __name__ == "__main__":
    PORT = 10000
    server_address = ("", PORT)
    try:
        with HTTPServer(server_address, WebHandler) as httpd:
            print(f"listening port {PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("^C received, shutting down the server")
