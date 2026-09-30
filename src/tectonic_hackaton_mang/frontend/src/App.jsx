import { Navigate, Outlet, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import Sidebar from './components/Sidebar'
import { useApp } from './context/AppContext'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import SignalDetail from './pages/SignalDetail'
import NotFound from './pages/NotFound'

function SiteLayout() {
  return (
    <>
      <Navbar />
      <Outlet />
      <Footer />
    </>
  )
}

function RequireAuth() {
  const { isAuthenticated, loading } = useApp()
  if (loading) {
    return (
      <div className="loading">
        <div className="spinner" />
        Sessie controleren…
      </div>
    )
  }
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <Outlet />
}

function AppShell() {
  return (
    <div className="container app-shell">
      <Sidebar />
      <main className="main">
        <Outlet />
      </main>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route element={<SiteLayout />}>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route element={<RequireAuth />}>
          <Route path="/app" element={<AppShell />}>
            <Route index element={<Dashboard />} />
            <Route path="signaal/:signalId" element={<SignalDetail />} />
          </Route>
        </Route>
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
