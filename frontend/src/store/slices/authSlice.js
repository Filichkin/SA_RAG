import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { authAPI } from '../../api/index';

// Async thunks
export const registerUser = createAsyncThunk(
  'auth/registerUser',
  async (userData, { rejectWithValue }) => {
    try {
      const response = await authAPI.register(userData);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Ошибка регистрации');
    }
  }
);

export const loginUser = createAsyncThunk(
  'auth/loginUser',
  async (credentials, { rejectWithValue }) => {
    try {
      const response = await authAPI.login(credentials);
      console.log('loginUser thunk: получен ответ от API:', response);
      return response; // Убираем .data, так как API уже возвращает объект напрямую
    } catch (error) {
      console.log('loginUser thunk: ошибка:', error);
      return rejectWithValue(error.response?.data?.detail || 'Ошибка входа');
    }
  }
);

export const verifyCode = createAsyncThunk(
  'auth/verifyCode',
  async ({ code, tempToken }, { rejectWithValue }) => {
    try {
      console.log('verifyCode thunk: отправляем код:', code, 'токен:', tempToken);
      const response = await authAPI.verifyCode(code, tempToken);
      console.log('verifyCode thunk: получен ответ:', response);
      return response;
    } catch (error) {
      console.log('verifyCode thunk: ошибка:', error);
      return rejectWithValue(error.response?.data?.detail || 'Ошибка проверки кода');
    }
  }
);

export const logoutUser = createAsyncThunk(
  'auth/logoutUser',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authAPI.logout();
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Ошибка выхода');
    }
  }
);

export const getCurrentUser = createAsyncThunk(
  'auth/getCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authAPI.getCurrentUser();
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Ошибка получения данных пользователя');
    }
  }
);

const initialState = {
  user: null,
  token: localStorage.getItem('token'),
  tempToken: null,
  isAuthenticated: !!localStorage.getItem('token'),
  isLoading: false,
  error: null,
  loginStep: 'credentials', // 'credentials' | 'verification'
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setLoginStep: (state, action) => {
      state.loginStep = action.payload;
    },
    clearTempToken: (state) => {
      state.tempToken = null;
    },
  },
  extraReducers: (builder) => {
    // Register
    builder
      .addCase(registerUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload;
        state.error = null;
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      });

    // Login (first step)
    builder
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        console.log('LoginUser fulfilled:', action.payload);
        state.isLoading = false;
        state.tempToken = action.payload.temp_token;
        state.loginStep = 'verification';
        state.error = null;
      })
      .addCase(loginUser.rejected, (state, action) => {
        console.log('LoginUser rejected:', action.payload);
        state.isLoading = false;
        state.error = action.payload;
      });

    // Verify code (second step)
    builder
      .addCase(verifyCode.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(verifyCode.fulfilled, (state, action) => {
        state.isLoading = false;
        state.token = action.payload.access_token;
        state.isAuthenticated = true;
        state.loginStep = 'credentials';
        state.tempToken = null;
        localStorage.setItem('token', action.payload.access_token);
        state.error = null;
        // Получаем данные пользователя после успешной аутентификации
        // Это будет выполнено в компоненте через useEffect
      })
      .addCase(verifyCode.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      });

    // Logout
    builder
      .addCase(logoutUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(logoutUser.fulfilled, (state) => {
        state.isLoading = false;
        state.user = null;
        state.token = null;
        state.tempToken = null;
        state.isAuthenticated = false;
        state.loginStep = 'credentials';
        localStorage.removeItem('token');
        state.error = null;
      })
      .addCase(logoutUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      });

    // Get current user
    builder
      .addCase(getCurrentUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(getCurrentUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(getCurrentUser.rejected, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = false;
        state.token = null;
        localStorage.removeItem('token');
        state.error = action.payload;
      });
  },
});

export const { clearError, setLoginStep, clearTempToken } = authSlice.actions;
export default authSlice.reducer;
