import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link, useNavigate } from 'react-router-dom';
import { loginUser, verifyCode, clearError, setLoginStep, getCurrentUser } from '../store/slices/authSlice';

const Login = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loginStep, isLoading, error, tempToken } = useSelector((state) => state.auth);
  
  const [credentials, setCredentials] = useState({
    email: '',
    password: '',
  });
  
  const [code, setCode] = useState('');

  const handleCredentialsSubmit = async (e) => {
    e.preventDefault();
    console.log('Отправляем данные для входа:', credentials);
    const result = await dispatch(loginUser(credentials));
    if (result.payload && result.payload.temp_token) {
      navigate('/two-factor-auth');
    }
  };

  const handleCodeSubmit = async (e) => {
    e.preventDefault();
    const result = await dispatch(verifyCode({ code, tempToken }));
    if (result.payload && result.payload.access_token) {
      // Получаем данные пользователя после успешной аутентификации
      await dispatch(getCurrentUser());
      navigate('/');
    }
  };

  const handleBackToCredentials = () => {
    dispatch(setLoginStep('credentials'));
    dispatch(clearError());
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    if (loginStep === 'credentials') {
      setCredentials(prev => ({ ...prev, [name]: value }));
    } else {
      setCode(value);
    }
  };

  if (loginStep === 'verification') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
              Подтверждение входа
            </h2>
            <p className="mt-2 text-center text-sm text-gray-600">
              Введите 6-значный код, отправленный на вашу почту
            </p>
            <p className="mt-1 text-center text-xs text-blue-600">
              💡 Для разработки: код отображается в консоли сервера
            </p>
          </div>
          <form className="mt-8 space-y-6" onSubmit={handleCodeSubmit}>
            <div>
              <label htmlFor="code" className="sr-only">
                Код подтверждения
              </label>
              <input
                id="code"
                name="code"
                type="text"
                required
                maxLength="6"
                value={code}
                onChange={handleInputChange}
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm text-center text-2xl tracking-widest"
                placeholder="000000"
              />
            </div>

            {error && (
              <div className="text-red-600 text-sm text-center">
                {typeof error === 'string' ? error : JSON.stringify(error)}
              </div>
            )}

            <div className="flex space-x-4">
              <button
                type="button"
                onClick={handleBackToCredentials}
                className="group relative w-full flex justify-center py-2 px-4 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Назад
              </button>
              <button
                type="submit"
                disabled={isLoading || code.length !== 6}
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Проверка...' : 'Подтвердить'}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Вход в систему
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Войдите в свой аккаунт
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleCredentialsSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email" className="sr-only">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={credentials.email}
                onChange={handleInputChange}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Email адрес"
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Пароль
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={credentials.password}
                onChange={handleInputChange}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Пароль"
              />
            </div>
          </div>

          {error && (
            <div className="text-red-600 text-sm text-center">
              {typeof error === 'string' ? error : JSON.stringify(error)}
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Вход...' : 'Войти'}
            </button>
          </div>
        </form>
        
        <div className="text-center mt-6 space-y-2">
          <p className="text-sm text-gray-600">
            Нет аккаунта?{' '}
            <Link to="/register" className="font-medium text-indigo-600 hover:text-indigo-500">
              Зарегистрироваться
            </Link>
          </p>
          <p className="text-sm text-gray-600">
            Забыли пароль?{' '}
            <Link to="/reset-password" className="font-medium text-red-600 hover:text-red-500">
              Сбросить пароль
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
