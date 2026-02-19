# TCG Arena — Force of Will Integration

This repository provides all necessary files to play **Force of Will (FoW)** on [TCG Arena](https://www.tcg-arena.fr/), a free browser-based platform for playing trading card games online.

## What is this?

[Force of Will](https://www.fowtcg.com/) is a competitive trading card game published by Eye Spy Productions. While there is no official digital client, this project integrates the full FoW card pool into TCG Arena, allowing players to build decks and play matches against each other online for free.

## Contents

| File / Folder | Description |
|---|---|
| `cards.json` | Full Force of Will card data |
| `cards_fow.json` | FoW-specific card definitions formatted for TCG Arena |
| `custom_cards.json` | Custom or community cards |
| `decks.json` | Sample/starter decks |
| `Game_FOW.json` | Game configuration file for TCG Arena |
| `image_cache.json` | Cached card image references |
| `missing_images.txt` | List of cards currently missing card art |
| `convert_cards.py` | Python script used to convert and process card data |
| `Images/` | Card and token images |
| `tokens/` | Token card images |

## How to Use

Head over to [TCG Arena](https://www.tcg-arena.fr/) and follow their instructions for loading a custom game. The files in this repository are the data source that powers the Force of Will game mode on the platform.

> **Note:** TCG Arena is a third-party platform not affiliated with Eye Spy Productions. This project is a community effort to bring Force of Will to an accessible online play environment.

## Updating the Card Data

The `convert_cards.py` script is used to process raw card data and generate the JSON files used by TCG Arena. If you want to contribute updated card data:

1. Clone the repository
2. Update the source card data
3. Run `python convert_cards.py`
4. Submit a pull request with the updated JSON files

## Contributing

Missing a card? Found incorrect card data or a broken image? Feel free to open an **Issue** or submit a **Pull Request**. Contributions are welcome, especially for:

- New set releases
- Missing or incorrect card images
- Card text / rules corrections

## Community

This project was built by and for the Force of Will community. If you play FoW and want to help test, report bugs, or contribute card data, join the conversation in the FoW community Discord or reach out via GitHub Issues.

---

*This is an unofficial fan project. Force of Will and all related assets are the property of Eye Spy Productions.*
