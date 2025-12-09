# AdVision AI - Frontend

Next.js 14 frontend for AdVision AI marketing intelligence platform.

## Features

- 🔐 JWT Authentication (Login/Register)
- 📊 Dashboard with Analytics Charts
- 🎯 Campaign Management
- 🎨 Creative Upload & Management
- 🛡️ AI Trust Score Badges
- 📈 ROI Calculations & Predictions
- 🎨 Tailwind CSS Styling
- 📱 Responsive Design

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **State**: React Hooks

## Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### 4. Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
src/
├── app/
│   ├── page.tsx              # Home (redirects)
│   ├── layout.tsx            # Root layout
│   ├── globals.css           # Global styles
│   ├── login/
│   │   └── page.tsx          # Login page
│   ├── register/
│   │   └── page.tsx          # Register page
│   ├── dashboard/
│   │   └── page.tsx          # Dashboard with charts
│   └── campaigns/
│       └── page.tsx          # Campaign management
├── components/
│   ├── Navbar.tsx            # Navigation bar
│   └── TrustScoreBadge.tsx   # AI Trust Score badge
└── lib/
    ├── api.ts                # API client & endpoints
    └── auth.ts               # Auth utilities
```

## Pages

### 1. Login (`/login`)
- Email/password authentication
- JWT token storage
- Redirect to dashboard

### 2. Register (`/register`)
- User registration
- Organization creation
- Auto-login after signup

### 3. Dashboard (`/dashboard`)
- Total campaigns, spend, revenue
- Average CTR & ROI
- Platform breakdown (Pie chart)
- Top campaigns (Bar chart)
- ROI summary

### 4. Campaigns (`/campaigns`)
- List all campaigns
- Create new campaign
- View campaign metrics
- Predict engagement (ML)
- Delete campaigns

## Components

### Navbar
- Logo & navigation links
- Logout button
- Responsive design

### TrustScoreBadge
- Visual trust score indicator
- 4 levels: High (90+), Medium (70-89), Low (50-69), Risk (<50)
- Color-coded badges
- Icons for each level

## API Integration

All API calls use Axios with:
- Automatic JWT token injection
- 401 error handling (auto-logout)
- Base URL from environment

### Endpoints Used

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user
- `GET /campaigns/` - List campaigns
- `POST /campaigns/` - Create campaign
- `DELETE /campaigns/{id}` - Delete campaign
- `GET /analytics/dashboard` - Dashboard stats
- `POST /ml/predict-engagement` - Predict engagement

## Styling

- **Tailwind CSS** for utility-first styling
- **Custom colors**: Primary blue theme
- **Responsive**: Mobile-first design
- **Dark mode**: Ready (prefers-color-scheme)

## Deployment

### Vercel (Recommended - FREE)

1. Push to GitHub
2. Import project in Vercel
3. Add environment variable: `NEXT_PUBLIC_API_URL`
4. Deploy!

### Docker

```bash
docker build -t advision-frontend .
docker run -p 3000:3000 advision-frontend
```

## Development Tips

- Use `npm run dev` for hot reload
- Check console for API errors
- JWT token stored in cookies
- Auto-redirect if not authenticated

## Future Enhancements

- [ ] Creative upload UI
- [ ] Trust score details page
- [ ] Advanced analytics filters
- [ ] Real-time updates
- [ ] Dark mode toggle
- [ ] Multi-language support
