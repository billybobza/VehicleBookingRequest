# Car Booking System - Frontend

This is the frontend application for the car booking system, built with Svelte 5 and TypeScript.

## Features

- **Svelte 5** with TypeScript for type safety
- **Routing** using svelte-spa-router
- **API Service Layer** for backend communication
- **Error Handling** with user-friendly error display
- **Loading State Management** for better UX
- **Testing** with Vitest

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── BookingForm.svelte
│   ├── ErrorDisplay.svelte
│   └── LoadingSpinner.svelte
├── services/           # API and external services
│   └── api.ts
├── stores/             # Svelte stores for state management
│   └── ui.ts
├── tests/              # Test files
│   ├── api.test.ts
│   └── ui-stores.test.ts
├── utils/              # Utility functions
│   └── async.ts
├── App.svelte          # Main app component
├── main.ts             # App entry point
└── routes.ts           # Route definitions
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm test` - Run tests
- `npm run test:watch` - Run tests in watch mode

## API Integration

The frontend communicates with the FastAPI backend through the API service layer (`src/services/api.ts`). The service handles:

- Vehicle management (get all vehicles, get available vehicles)
- Booking management (create booking, get booking details)
- Error handling and response formatting
- Type safety with TypeScript interfaces

## Error Handling

The application includes comprehensive error handling:

- **API Errors**: Automatically displayed to users with friendly messages
- **Network Errors**: Handled gracefully with retry options
- **Validation Errors**: Form validation with inline error display
- **Loading States**: Visual feedback during async operations

## State Management

The application uses Svelte stores for state management:

- **Loading Store**: Manages loading states for different operations
- **Error Store**: Handles error display and auto-removal
- **UI Store**: General UI state management

## Development

The frontend is configured to proxy API requests to the backend running on `http://localhost:8000`. Make sure the backend is running when developing the frontend.

## Testing

Tests are written using Vitest and cover:

- API service functionality
- Store behavior
- Utility functions
- Component logic (where applicable)

Run tests with `npm test` or `npm run test:watch` for continuous testing.