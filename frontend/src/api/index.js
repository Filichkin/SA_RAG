const API_BASE_URL = 'http://127.0.0.1:8000';

class AuthAPI {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw {
        response: {
          data: errorData,
          status: response.status,
        },
      };
    }

    return response.json();
  }

  // Регистрация пользователя
  async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  // Первый этап входа (email + пароль)
  async login(credentials) {
    console.log('API: Отправляем запрос на /auth/2fa/login с данными:', credentials);
    const response = await this.request('/auth/2fa/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    console.log('API: Получен ответ:', response);
    return response;
  }

  // Второй этап входа (проверка кода)
  async verifyCode(code, tempToken) {
    console.log('API: Отправляем код:', code, 'с токеном:', tempToken);
    
    const response = await this.request('/auth/2fa/verify-code', {
      method: 'POST',
      headers: {
        'X-Temp-Token': tempToken,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
    });
    console.log('API: Получен ответ на проверку кода:', response);
    return response;
  }

  // Выход из системы
  async logout() {
    const token = localStorage.getItem('token');
    return this.request('/auth/logout', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  // Получение информации о текущем пользователе
  async getCurrentUser() {
    const token = localStorage.getItem('token');
    return this.request('/users/me', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  // Сброс пароля
  async resetPassword(email) {
    console.log('API: Отправляем запрос на сброс пароля для:', email);
    const response = await this.request('/users/reset-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
    console.log('API: Получен ответ на сброс пароля:', response);
    return response;
  }

  // Отправка запроса к AI ассистенту с поддержкой стриминга
  async askWithAI(query, onChunk, onError, onComplete) {
    const token = localStorage.getItem('token');
    const url = `${this.baseURL}/ask_with_ai`;
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`HTTP ${response.status}: ${errorData.detail || 'Ошибка сервера'}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) {
            onComplete && onComplete();
            break;
          }

          const chunk = decoder.decode(value, { stream: true });
          onChunk && onChunk(chunk);
        }
      } finally {
        reader.releaseLock();
      }
    } catch (error) {
      console.error('Ошибка при запросе к AI:', error);
      onError && onError(error);
    }
  }
}

export const authAPI = new AuthAPI();
