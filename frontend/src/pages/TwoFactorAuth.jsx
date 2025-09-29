import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { verifyCode, getCurrentUser } from '../store/slices/authSlice';

const TwoFactorAuth = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { isLoading, error, tempToken } = useSelector((state) => state.auth);
  
  const [code, setCode] = useState('');

  const handleCodeSubmit = async (e) => {
    e.preventDefault();
    const result = await dispatch(verifyCode({ code, tempToken }));
    if (result.payload && result.payload.access_token) {
      // Получаем данные пользователя после успешной аутентификации
      await dispatch(getCurrentUser());
      navigate('/');
    }
  };

  const handleInputChange = (e) => {
    setCode(e.target.value);
  };

  return (
    <div className="flex items-center justify-center min-h-screen px-4 py-12 bg-gray-50 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div>
          <h2 className="mt-6 text-3xl font-extrabold text-center text-gray-900">
            Подтверждение входа
          </h2>
          <p className="mt-2 text-sm text-center text-gray-600">
            Введите 6-значный код, отправленный на вашу почту
          </p>
          <p className="mt-1 text-xs text-center text-blue-600">
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
              className="relative block w-full px-3 py-2 text-2xl tracking-widest text-center text-gray-900 placeholder-gray-500 border border-gray-300 rounded-md appearance-none focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="000000"
            />
          </div>

          {error && (
            <div className="text-sm text-center text-red-600">
              {typeof error === 'string' ? error : JSON.stringify(error)}
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={isLoading || code.length !== 6}
              className="relative flex justify-center w-full px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md group hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Проверка...' : 'Подтвердить'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TwoFactorAuth;
