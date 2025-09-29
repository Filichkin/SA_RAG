import { useSelector, useDispatch } from 'react-redux';
import { logoutUser } from '../store/slices/authSlice';

function Header() {
  const dispatch = useDispatch();
  const { isAuthenticated, user } = useSelector((state) => state.auth);

  const handleLogout = () => {
    dispatch(logoutUser());
  };

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <img className="h-8 w-auto" src="/logo.svg" alt="logo" />
            <h1 className="ml-4 text-xl font-semibold text-gray-900">
              Чат-бот
            </h1>
          </div>
          
          {isAuthenticated ? (
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Добро пожаловать, {user?.first_name || 'Пользователь'}!
              </span>
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Выйти
              </button>
            </div>
          ) : (
            <nav>
              <ul className="flex gap-6">
                <li>
                  <span className="text-gray-700 font-medium">Главная</span>
                </li>
                <li>
                  <span className="text-gray-700 font-medium">О нас</span>
                </li>
                <li>
                  <span className="text-gray-700 font-medium">Контакты</span>
                </li>
              </ul>
            </nav>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header;
