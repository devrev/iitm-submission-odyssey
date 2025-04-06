# DEVREV Spotify Agent  
## Summary  
**Madhav and Pranjal: Team-Artificially insecure**

🎬 [Watch Demo Video](https://drive.google.com/file/d/1YxCuCsGO79NWW9Ux-yoAQMwOxREP6x0U/view?usp=sharing)

---

## Introduction

The **Spotify Web API** offers developers extensive capabilities to access and control music, playlists, playback devices, and artist data.

This project leverages **DevRev’s Agent Framework** to create a custom conversational agent that integrates with Spotify. Users can play music, retrieve artist information, and manage playback through chat-based interactions.

At its core, this integration uses **OAuth 2.0** to provide secure access without compromising user credentials. The agent handles token generation, refreshes expired tokens, and remembers authorized devices for a seamless experience.

---

## Functionalities

This section outlines the core functionalities of the Spotify Integration Agent. The agent provides an interactive and streamlined interface between the user and the Spotify Web API, facilitating music playback control, artist information retrieval, and seamless authorization management.

---

### 1. Account Setup and Authorization

- Guides the user to create a Spotify Developer Account.
- Collects essential credentials: `Client ID`, `Client Secret`, and `Redirect URL`.
- Generates an authorization URL for user login and consent.
- Extracts the authorization code from the redirect URL after user login.
- Exchanges the authorization code for an `access token` and stores the `refresh token` for long-term use.
- Automatically refreshes the access token when expired without re-prompting for credentials.

---

### 2. Device Management

- Retrieves a list of the user’s active Spotify devices.
- Allows the user to select a preferred device for playback control.

---

### 3. Artist Information Retrieval

- Accepts artist name queries from the user.
- Uses Spotify’s Search API to resolve artist name to artist ID.
- Retrieves and displays relevant artist data, including:
  - Artist name  
  - Genres  
  - Popularity score  
  - Follower count

---

### 4. Music Playback Control

- Accepts song name input from the user.
- Resolves song name to `track ID` using Spotify’s track search.
- Plays the selected track on the user’s chosen device.
- Supports the following playback controls:
  - **Pause Playback**: Temporarily halts the current song.
  - **Resume Playback**: Continues the song from the paused point.
  - **Next Track**: Skips to the next song in the queue.
  - **Previous Track**: Returns to the previous song.

---

### 5. Internal Token Handling

- Ensures the access token remains valid throughout the session.
- Utilizes the stored `refresh token` to acquire new access tokens as needed.
- Prevents unnecessary re-authentication by securely caching tokens.

---

Each of these functionalities is supported through modular skills, enabling a user-friendly and secure integration with Spotify’s Web API ecosystem.
