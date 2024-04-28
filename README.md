# InGenius AI Server

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)

## About <a name = "about"></a>

This is project gives ai support to InG project.

## Getting Started <a name = "getting_started"></a>

### Prerequisites

Choose one method to install the dependencies

- poetry (recommended)

```bash
poetry install --no-root
```

- pip

```bash
pip install -r requirements.txt
```

### Environment

App needs a `.env` file to connect `openai`

- Example

```env
OPENAI_API_KEY="<Your-OpenAI-KEY>"
OPENAI_ORG_ID="<Your-OrgId>"
```

## Configuration

### SQL Server

- Database configuration is in [database_config.py](./config/database_config.py)

## Usage <a name = "usage"></a>

```base
python main.py
```

## API Document (Swagger)
[http://localhost:8000/docs](http://localhost:8000/docs)
