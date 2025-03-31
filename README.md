# ComikNet-BE

**This project still in development, and the API is not stable yet.**

## Development

You should have the following installed:

- [uv package manager](https://github.com/astral-sh/uv)
- `MySQL` server(well configured)

Restore the specified version of the python:

```bash
uv python install
```

If you develop on Linux, you have to install mysql's development package.

For Debian/Ubuntu:

```bash
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential pkg-config
```

For Red Hat / CentOS:

```bash
sudo yum install python3-devel mysql-devel pkgconfig
```

Restore the dependencies(Include the plugins' dependencies):

```bash
uv sync --all-packages
```

Modify the configuration file located at `Services/Config/config.toml.sample` and rename it to `config.toml`.

You can generate the secret key by using the `openssl rand -hex 32` command.

## Run the server

```bash
uv run uvicorn main:app
```
