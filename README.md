# Frontier Game Bot

A robust and feature-rich **Telegram game bot** designed for group fun and user engagement. The bot blends coins, trivia, banking, guilds, betting, and admin tools within a modern, modular Python architecture.

---

## Features

- **Economy:** Earn, spend, deposit, and withdraw coins.
- **Banking:** Deposit coins for interest, check balances, and manage funds.
- **Betting:** Gamble coins with risk/reward systems and play limits.
- **Trivia:** Play anime/general trivia for coin rewards.
- **Mini-Games:** Dice, dart, and various Telegram-integrated games.
- **Guilds:** Create, join, manage, and compete in guilds with leveling.
- **Daily Bonuses:** Claim daily rewards and other achievement-based incentives.
- **Admin Tools:** Eval, user moderation.
- **Scheduled Tasks:** Automated daily payouts, cooldown resets, and more.
- **Modern Interactions:** Inline keyboards, asynchronous event handling.

---

## Setup & Installation

### Prerequisites

- Python 3.10 or newer.
- MongoDB database (local or cloud).
- Telegram bot token.

### Environment Variables

Set the following in your OS or a `.env` file:


## Bot Commands

| Command               | Description                                 |
|-----------------------|---------------------------------------------|
| `/start`              | Register and start using the bot            |
| `/ping`               | Bot status and uptime                       |
| `/deposit <amt>`      | Deposit coins to bank                       |
| `/withdraw <amt>`     | Withdraw coins from bank                    |
| `/checkbank`          | Display your bank/interest stats            |
| `/bet <amt>`          | Bet coins; risk & reward!                   |
| `/daily`              | Get daily coin reward                       |
| `/profile`            | View your stats and coin history            |
| `/trivia`             | Play fun trivia games                       |
| `/dart`               | Play dart mini-game for coins               |
| `/dice` or `/dice2`   | Wager coins in dice games                   |
| `/guild`              | Manage/join/leave your guild                |
| `/backup`             | Admin DB backup (admins only)               |
| `/eval`               | Run code as admin (restricted)              |

### Guild Subcommands

- `/guild create <name>`
- `/guild join <name>`
- `/guild leave`
- `/guild info`
- `/guild transfer <username>`
- `/guild delete`
- `/guild requests`
- `/guild approve <username>`

---

## Games & Banking

### Betting

- Use `/bet <amount>` to wager coins. Win or lose based on a random chance.
- Limited by daily play caps and minimum required balance.

### Dice

- `/dice` or `/dice2` to play dice roll with coins. High roll may win extra coins!

### Trivia

- `/trivia` to answer anime or general trivia.
- Earn coins for correct answers; use callbacks to answer in chat.

### Banking

- `/deposit <amount>` and `/withdraw <amount>` handle your coins and earn interest over time.

### Daily

- `/daily` once per 24 hours to receive a randomized bonus.

---

## Guild System

- **Create** a new guild with `/guild create <name>`.
- **Join/leave** guilds with `/guild join <name>` and `/guild leave`.
- **Manage** members, approve join requests, and **transfer** or **delete** guilds.

---

## Admin Tools

- `/backup` to download up-to-date MongoDB backups.
- `/eval <code>` for trusted developer evaluation.
- Guild, game, bank, and trivia controls accessible only with specific roles.

---

## Architecture

- **Tech:** Python 3 (async), Pyrogram, PyMongo.
- **Plugins:** Modularity via `Frontier/Plugins/` submodules.
- **DB:** Users/coins/guilds stored in MongoDB.
- **Config:** Adjustable rates, permissions, and tasks via `Helpers/vars.py`.

---

## Contributing

1. Fork and clone this repo.
2. Make edits or add feature plugins to `Frontier/Plugins/`.
3. Expand trivia questions via `Helpers/triviaque.py` or `Plugins/triviaquestions.py`.
4. PRs are welcome!

## Author

siamkira

---

## License

MIT License. See `LICENSE` file if present.

---