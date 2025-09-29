import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { verifyCode, clearError } from '../store/slices/authSlice';

const TwoFactorAuth = () => {
  const dispatch = useDispatch();
  const { isLoading, error, tempToken } = useSelector((state) => state.auth);
  
  const [code, setCode] = useState('');

  const handleCodeSubmit = async (e) => {
    e.preventDefault();
    dispatch(verifyCode({ code, tempToken }));
  };

  const handleInputChange = (e) => {
    setCode(e.target.value);
  };

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

          <div>
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
};

export default TwoFactorAuth;
