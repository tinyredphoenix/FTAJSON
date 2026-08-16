# FTAJSON 🇮🇳

Curated, high-uptime Indian Free-to-Air (FTA), 24/7 News, Devotional, Infotainment, and Music Live HLS Streams.

## 📡 Endpoints
* **JSON Format**: `https://raw.githubusercontent.com/tinyredphoenix/FTAJSON/main/fta_channels.json`
* **M3U Playlist Format**: `https://raw.githubusercontent.com/tinyredphoenix/FTAJSON/main/playlist.m3u`

---

## ⚡ Automated Health Checks & Auto-Repair
* **Automated Cron**: A GitHub Action runs **every 12 hours** to probe all stream endpoints for active HTTP 200 HLS status.
* **Auto-Repair**: If an upstream Akamai/CloudFront CDN rotates or changes, the workflow automatically finds updated streams from upstream and commits the changes.

---

## 📺 Channel Categories (60 Verified HD Streams)
1. **Doordarshan**: DD National HD, DD Sports HD, DD Kisan, DD Punjabi
2. **Hindi News**: Aaj Tak HD, ABP News HD, NDTV India HD, News18 India HD, Republic Bharat HD, Times Now Navbharat HD, Zee News HD, Zee Bharat HD, Zee Salaam HD, TV9 Bharatvarsh HD, India TV, Good News Today HD, Bharat24 HD, Sudarshan News HD
3. **English News**: NDTV 24x7 HD, CNN-News18 HD, Republic TV HD
4. **Business & Markets**: NDTV Profit HD, CNBC TV18 HD, CNBC TV18 Prime HD, CNBC Awaaz HD, CNBC Bajar HD, Zee Business, ET Now Swadesh
5. **Infotainment & Lifestyle**: Travelxp HD, EPIC TV HD, DocuBay HD, INWILD HD, InWonder HD, Food Food
6. **Music**: 9XM HD, 9X Jalwa HD, 9X Tashan HD, 9X Jhakaas HD, B4U Music
7. **Movies & Entertainment (FTA)**: Shemaroo TV, Zee Cine Classic HD, Zee Comedy Nation HD
8. **Devotional & Spiritual**: Paras TV, Sanskar TV HD, Satsang TV HD, Aastha Bhajan HD, Arihant TV, Vedic TV, Sadhna TV, Jinvani Channel, Total Bhakti HD
9. **Regional**: Gangaur TV HD, Zee Rajasthan HD, News18 Rajasthan HD, First India News HD, ABP Ganga HD, ABP Ananda HD, Zee 24 Taas HD, Zee Delhi NCR Haryana HD, Zee Bihar Jharkhand HD
