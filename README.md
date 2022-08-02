# Shodo Python CLI

## Installation

```bash
$ pip3 install shodo
```

## Configuration

These environment variables are required

* `SHODO_API_ROOT` Root endpoint for API (like `https://api.shodo.ink/@my-organization/my-project/`).
* `SHODO_API_TOKEN` Token to access each projects (Access to Shodo and see projects' 「API連携」 settings page)

## Usage

Lint Japanese.
This command requires authentication (API root and a token) for Lint API projects (not for writing).

```bash
$ shodo lint filename.md
```

```bash
$ shodo lint ./demo/demo.md                                                                                          15:18:27
18:4 ら抜き言葉です
     てください。 すぐに食べれる（→ 食べられる）。 
...
3:11 もしかしてAI
     飛行機の欠便があり、運行（→ 運航）状況が変わった。 バ
6:5 もしかしてAI
     ません。  これが私で（→ の）自己紹介です。  こ
12:11 もしかしてAI
     なんでも問題を解決しい（→ トル）ます。 日本語ののよ
```

### Download files

Download all of Markdown posts and images!

```bash
$ shodo download --target=docs
```

Options:

```
Usage: shodo download [OPTIONS]

Options:
  --target TEXT      Target directory to save files
  --in-tree BOOLEAN  Download only files with task Folder
  --help             Show this message and exit.
```
