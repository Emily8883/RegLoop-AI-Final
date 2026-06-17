# RegLoop AI - Dashboard Frontend

**Modern React-based compliance dashboard for RegLoop AI platform**

Built with Next.js 15.5.6, React 19.1.1, TypeScript, and Tailwind CSS.

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation & Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

---

## 📁 Project Structure

```
frontend/
├── app/
│   ├── page.tsx                 # Dashboard landing page
│   ├── layout.tsx               # Root layout with metadata
│   ├── globals.css              # Modern design system (1400+ lines)
│   ├── documents/
│   │   └── page.tsx            # Document management page
│   ├── obligations/
│   │   └── page.tsx            # Obligations tracking page
│   ├── compliance/              # Compliance analytics (expandable)
│   ├── dashboard/               # Dashboard components (expandable)
│   └── components/              # Reusable components
│       ├── DocumentTable.tsx
│       ├── ObligationTable.tsx
│       ├── DashboardCards.tsx
│       ├── ComplianceChart.tsx
│       └── PriorityChart.tsx
├── services/
│   └── api.ts                   # API client wrapper
├── types/
│   └── index.ts                 # TypeScript interfaces
├── constants/
│   └── config.ts                # Configuration constants
├── public/                      # Static assets
├── package.json
├── tsconfig.json
├── next.config.ts
├── postcss.config.mjs
├── eslint.config.mjs
└── README.md                    # This file
```

---

## 🎨 Modern Design System

### Features
- **Spacing System**: 7-level hierarchy (xs → 3xl) for generous layouts
- **Color Palette**: Modern semantic naming with 13+ colors
- **Shadows**: 4-level depth system for visual hierarchy
- **Animations**: 8 modern keyframes (fadeIn, slideInUp, scaleIn, glow, etc.)
- **Border Radius**: Configurable from sm to xl
- **Dark Mode**: Full support with optimized colors
- **Responsive**: Mobile-first design approach

### Key Utilities
- `.card` - Modern card styling
- `.badge`, `.badge-success`, `.badge-warning`, `.badge-danger`, `.badge-info` - Status indicators
- `.container-modern` - Consistent max-width container
- Animation classes: `.animate-fadeIn`, `.animate-slideInUp`, `.animate-scaleIn`, etc.

---

## 📖 Pages

### Dashboard (`/`)
- **KPI Cards**: Documents count, obligations count, compliance score
- **Analytics Section**: Charts for obligations by category and priority breakdown
- **Activity Feed**: Recent documents and obligations tables
- **API Status**: Connection status banner

### Documents (`/documents`)
- **Document List**: All uploaded documents with metrics
- **Columns**: Filename, obligations count, file size, upload date
- **Features**: Responsive table, file size formatting, date display

### Obligations (`/obligations`)
- **Obligation List**: All extracted obligations
- **Filters**: By priority (high/medium/low) and category
- **Columns**: Priority badge, category, responsible team, obligation text
- **Features**: Real-time filtering, status indicators

---

## 🔌 API Integration

### API Client (`services/api.ts`)

```typescript
// Example usage
const response = await apiClient.getDocuments();
const obligations = await apiClient.getObligations();
const summary = await apiClient.getComplianceSummary();
```

### Available Methods
- `getDocuments()` - List all documents
- `getObligations(filters?)` - Query obligations
- `getComplianceSummary()` - Get compliance metrics
- `getGapAnalysis()` - Get gap analysis
- `uploadDocument(file)` - Upload document
- `analyzDocument(documentId)` - Trigger analysis

### Backend Connection
- **URL**: `http://127.0.0.1:8000`
- **CORS**: Configured for localhost:3000
- **Protocol**: REST API with JSON

---

## 🛠️ Development Commands

```bash
# Run development server with hot reload
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Run ESLint
npm run lint

# Format code (if prettier configured)
npm run format
```

---

## 📦 Dependencies

### Core
- **next**: 15.5.6 - React framework
- **react**: 19.1.1 - UI library
- **typescript**: 5.x - Type safety

### Styling
- **tailwindcss**: Utility-first CSS framework
- **postcss**: CSS transformation
- **postcss-preset-env**: Modern CSS support

### Development
- **eslint**: Linting
- **eslint-config-next**: Next.js linting config

---

## 🎯 Component Architecture

### Page Components
- Use server components by default
- Use `"use client"` for interactive components
- Fetch data in server components when possible

### Reusable Components
Located in `app/components/`:
- **DashboardCards** - KPI metric cards
- **DocumentTable** - Document listing
- **ObligationTable** - Obligation listing
- **ComplianceChart** - Category distribution chart
- **PriorityChart** - Priority breakdown chart

### Props & Types
All components have TypeScript interfaces in `types/index.ts`:
```typescript
interface Document {
  id: number;
  filename: string;
  obligations_count: number;
  text_length: number;
  uploaded_at: string;
}

interface Obligation {
  id: number;
  document_id: number;
  obligation_text: string;
  category: string;
  priority: string;
  responsible_team: string;
}
```

---

## 🌙 Dark Mode

The dashboard supports dark mode through Next.js built-in support:
- CSS custom properties handle light/dark switching
- Use `dark:` Tailwind prefix for dark mode styles
- Automatic dark mode detection and toggle

---

## 🔐 Security

### Environment Variables
Create `.env.local` for sensitive data:
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### Best Practices
- ✅ Input validation on all forms
- ✅ Error handling for API failures
- ✅ Secure API client configuration
- ✅ CORS properly configured

---

## 📱 Responsive Design

- **Mobile**: Optimized for small screens
- **Tablet**: Flexible grid layouts
- **Desktop**: Full feature set
- **Breakpoints**: Tailwind defaults (sm, md, lg, xl, 2xl)

---

## 🧪 Testing

### API Testing
```bash
# Backend must be running on 127.0.0.1:8000
npm run dev
# Visit http://localhost:3000
```

### Manual Testing Checklist
- [ ] Dashboard loads correctly
- [ ] KPI cards display proper data
- [ ] Charts render without errors
- [ ] Documents page shows uploaded files
- [ ] Obligations page loads obligations
- [ ] Filters work on obligations page
- [ ] Dark mode toggle works (if implemented)
- [ ] Responsive design works on mobile

---

## 🐛 Troubleshooting

### Frontend won't start
```bash
# Clear cache and reinstall
rm -r node_modules .next
npm install
npm run dev
```

### API connection errors
- Verify backend is running: `http://127.0.0.1:8000`
- Check CORS configuration in backend
- Verify `NEXT_PUBLIC_API_URL` is correct

### Styling issues
- Clear Next.js cache: `rm -r .next`
- Rebuild Tailwind: `npm run build`
- Check `globals.css` for custom styles

---

## 📚 Additional Resources

### Documentation
- [Main README](../README.md) - Full project overview
- [Backend Documentation](../backend/README_DELIVERY.md) - API details
- [Setup Guide](../backend/COMPLETE_SETUP_GUIDE.md) - Complete setup
- [API Docs](http://127.0.0.1:8000/docs) - Swagger UI

### Learning Resources
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)

---

## 🚀 Deployment

### Vercel (Recommended for Next.js)
1. Push code to GitHub
2. Connect repository to Vercel
3. Set environment variables
4. Deploy

### Other Platforms
```bash
npm run build
npm run start
```

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -m 'feat: add your feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Open Pull Request

---

## 📄 License

Part of RegLoop AI platform - Compliance Management System

---

## 📞 Support

For issues or questions:
1. Check the main [README.md](../README.md)
2. Review [API documentation](../backend/README_DELIVERY.md)
3. Check backend logs for errors

---

**Dashboard Ready for Production! 🎉**

Last Updated: June 10, 2026
