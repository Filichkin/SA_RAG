import React, { useEffect } from 'react';
import { Provider, useSelector, useDispatch } from 'react-redux';
import { store } from './store/store';
import Login from './pages/Login';
import Register from './pages/Register';
import Home from './pages/Home';
import Layout from './components/Layout';
import { getCurrentUser } from './store/slices/authSlice';

function AppContent() {
  const dispatch = useDispatch();
  const { isAuthenticated, user, isLoading } = useSelector((state) => state.auth);
  const [currentView, setCurrentView] = React.useState('login');

  useEffect(() => {
    // Проверяем, есть ли токен в localStorage при загрузке
    const token = localStorage.getItem('token');
    if (token && !user) {
      dispatch(getCurrentUser());
    }
  }, [dispatch, user]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка...</p>
        </div>
      </div>
    );
  }

  if (isAuthenticated) {
    return (
      <Layout>
        <Home />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gray-50">
        {currentView === 'login' ? (
          <div>
            <Login />
            <div className="text-center pb-8">
              <p className="text-sm text-gray-600">
                Нет аккаунта?{' '}
                <button
                  onClick={() => setCurrentView('register')}
                  className="font-medium text-indigo-600 hover:text-indigo-500"
                >
                  Зарегистрироваться
                </button>
              </p>
            </div>
          </div>
        ) : (
          <div>
            <Register />
            <div className="text-center pb-8">
              <p className="text-sm text-gray-600">
                Уже есть аккаунт?{' '}
                <button
                  onClick={() => setCurrentView('login')}
                  className="font-medium text-indigo-600 hover:text-indigo-500"
                >
                  Войти
                </button>
              </p>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}

function App() {
  return (
    <Provider store={store}>
      <AppContent />
    </Provider>
  );
}

export default App;
