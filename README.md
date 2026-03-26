# Billiards Scoring Web App

A modern, responsive billiards scoring system for two teams/players with real-time synchronization and persistent storage.

## Features

- **Split Screen Design**: Team A (blue) vs Team B (red) interface
- **Scoring System**: Cumulative scoring with numbers 1-15, maximum 60 points to win
- **Interactive Number Buttons**: White pill-shaped buttons that disappear when selected
- **Winner State**: Automatic winner detection with celebration animation
- **Undo Functionality**: Per-team undo with full history tracking
- **Persistent Storage**: Supabase integration for state persistence
- **Real-time Sync**: Auto-refresh every 5 seconds
- **Responsive Design**: Works on desktop and mobile devices
- **Reset Match**: Reset functionality with confirmation

## Tech Stack

- **Backend**: Python with FastAPI
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: Supabase (PostgreSQL)
- **Deployment**: Vercel
- **Styling**: Custom CSS with responsive design

## Setup Instructions

### 1. Supabase Setup

1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Go to the SQL Editor and run the following query to create the matches table:

```sql
CREATE TABLE matches (
    id INTEGER PRIMARY KEY DEFAULT 1,
    team_a_score INTEGER DEFAULT 0,
    team_b_score INTEGER DEFAULT 0,
    team_a_selected INTEGER[] DEFAULT '{}',
    team_b_selected INTEGER[] DEFAULT '{}',
    team_a_history INTEGER[] DEFAULT '{}',
    team_b_history INTEGER[] DEFAULT '{}',
    winner TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert initial row
INSERT INTO matches (team_a_score, team_b_score, team_a_selected, team_b_selected, team_a_history, team_b_history, winner)
VALUES (0, 0, '{}', '{}', '{}', '{}', NULL);
```

3. Go to Settings > API and copy:
   - Project URL
   - `anon` public API key

### 2. Environment Variables

For Vercel deployment, set these environment variables:
Name: SUPABASE_URL
Value: https://jwghlubvzolcpfydviaq.supabase.co

Name: SUPABASE_KEY  
Value: sb_publishable_CLgojMMPUH7DmMtt44iXiw_Kg1QzdqD
```
SUPABASE_URL=https://jwghlubvzolcpfydviaq.supabase.co
SUPABASE_KEY=sb_publishable_CLgojMMPUH7DmMtt44iXiw_Kg1QzdqD
```

### 3. Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables:
   ```bash
   # The .env file is already configured with your credentials
   # Or set them manually:
   export SUPABASE_URL=https://jwghlubvzolcpfydviaq.supabase.co
   export SUPABASE_KEY=sb_publishable_CLgojMMPUH7DmMtt44iXiw_Kg1QzdqD
   ```
4. Run the development server:
   ```bash
   uvicorn api.index:app --reload --host 0.0.0.0 --port 3000
   ```
5. Open `http://localhost:3000` in your browser

## Vercel Deployment

### Automatic Deployment

1. Push your code to GitHub
2. Connect your GitHub repository to Vercel
3. Set the environment variables in Vercel dashboard
4. Deploy

### Manual Deployment

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```
2. Set environment variables:
   ```bash
   vercel env add SUPABASE_URL
   # When prompted, enter: https://jwghlubvzolcpfydviaq.supabase.co
   
   vercel env add SUPABASE_KEY
   # When prompted, enter: sb_publishable_CLgojMMPUH7DmMtt44iXiw_Kg1QzdqD
   ```
3. Deploy:
   ```bash
   vercel --prod
   ```

## API Endpoints

### GET /api/match
Get current match state

**Response:**
```json
{
  "team_a_score": 25,
  "team_b_score": 30,
  "team_a_selected": [5, 10, 10],
  "team_b_selected": [15, 15],
  "team_a_history": [5, 10, 10],
  "team_b_history": [15, 15],
  "winner": null
}
```

### POST /api/score
Add score for a team

**Request:**
```json
{
  "team": "A",
  "number": 10
}
```

### POST /api/undo
Undo last score for a team

**Request:**
```json
{
  "team": "A"
}
```

### POST /api/reset
Reset the match

**Request:**
```json
{}
```

## Game Rules

1. Two teams (A and B) compete
2. Each team can select numbers from 1 to 15
3. Selected numbers are added to the team's cumulative score
4. Once a number is selected, it disappears from that team's available buttons
5. First team to reach 60 points wins
6. When a team wins, all number buttons are hidden and "Winner 🏆" is displayed
7. Undo can be used to revert the last score for each team independently
8. Match can be reset to start a new game

## File Structure

```
scoring/
├── api/
│   └── index.py              # FastAPI backend
├── public/
│   ├── index.html            # Main HTML file
│   ├── style.css             # Styling
│   └── script.js             # Frontend logic
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel configuration
└── README.md                # This file
```

## Customization

### Colors
- Team A (Blue): `#2563eb` in `style.css`
- Team B (Red): `#dc2626` in `style.css`

### Scoring Rules
- Maximum score: Change `60` to desired value in `api/index.py`
- Number range: Modify the loop in `script.js` (currently 1-15)

### Responsive Breakpoints
- Mobile: `768px` and `480px` in `style.css`

## Troubleshooting

### Common Issues

1. **Supabase Connection Error**
   - Verify environment variables are set correctly
   - Check Supabase project URL and API key

2. **CORS Issues**
   - Ensure Vercel domain is added to Supabase CORS settings

3. **Database Issues**
   - Verify the matches table exists with correct schema
   - Check if initial row was inserted

4. **Deployment Issues**
   - Ensure all environment variables are set in Vercel
   - Check Vercel deployment logs for errors

### Debug Mode

For debugging, you can open the browser console to see:
- API request/response logs
- Error messages
- State synchronization logs

## License

MIT License - feel free to use this project for personal or commercial purposes.
