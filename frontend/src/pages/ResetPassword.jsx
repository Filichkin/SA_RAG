import React, { useState } from 'react';

const ResetPassword = () => {
  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      console.log('Отправляем запрос на сброс пароля для:', email);
      
      const response = await fetch('/users/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      console.log('Ответ сервера:', response.status, response.statusText);

      if (response.ok) {
        const data = await response.json();
        console.log('Успешный ответ:', data);
        setIsSubmitted(true);
      } else {
        // Обработка ошибок
        let errorMessage = 'Произошла ошибка при сбросе пароля';
        
        try {
          const data = await response.json();
          console.log('Ошибка от сервера:', data);
          
          if (response.status === 404) {
            errorMessage = 'Пользователь с таким email не найден';
          } else {
            errorMessage = data.detail || errorMessage;
          }
        } catch (parseError) {
          console.error('Ошибка парсинга ответа:', parseError);
          errorMessage = `Ошибка сервера: ${response.status} ${response.statusText}`;
        }
        
        setError(errorMessage);
      }
    } catch (error) {
      console.error('Ошибка при сбросе пароля:', error);
      setError('Произошла ошибка при отправке запроса');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setEmail(e.target.value);
  };

  if (isSubmitted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
              <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
              Письмо отправлено
            </h2>
            <p className="mt-2 text-center text-sm text-gray-600">
              Мы отправили новый пароль на ваш email: <strong>{email}</strong>
            </p>
            <p className="mt-1 text-center text-xs text-gray-500">
              Проверьте папку "Спам", если письмо не пришло в течение нескольких минут
            </p>
          </div>
          <div className="mt-6">
            <button
              onClick={() => {
                setIsSubmitted(false);
                setEmail('');
              }}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-indigo-600 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Отправить еще раз
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Сброс пароля
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Введите ваш email для получения нового пароля
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email адрес
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={handleInputChange}
              className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Введите ваш email"
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-800">{error}</p>
                </div>
              </div>
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={isLoading || !email.trim()}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Отправка...' : 'Сбросить пароль'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ResetPassword;
