function Footer() {
  return (
    <footer className="bg-gray-800 text-white py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Support */}
          <div>
            <h3 className="mb-3 text-sm font-bold">
              Поддержка
            </h3>
            <ul className="space-y-2">
              <li>
                <span className="hover:text-gray-300 cursor-pointer">FAQ</span>
              </li>
              <li>
                <span className="hover:text-gray-300 cursor-pointer">Документация</span>
              </li>
              <li>
                <span className="hover:text-gray-300 cursor-pointer">Техническая поддержка</span>
              </li>
            </ul>
          </div>

          {/* Features */}
          <div>
            <h3 className="mb-3 text-sm font-bold">Возможности</h3>
            <ul className="space-y-2">
              <li>
                <span className="hover:text-gray-300 cursor-pointer">ИИ-ассистент</span>
              </li>
              <li>
                <span className="hover:text-gray-300 cursor-pointer">Безопасность</span>
              </li>
              <li>
                <span className="hover:text-gray-300 cursor-pointer">Интеграции</span>
              </li>
            </ul>
          </div>

          {/* Contact Information */}
          <div>
            <h3 className="mb-3 text-sm font-bold">Контакты</h3>
            <p className="text-sm text-gray-300">Email: support@chatbot.com</p>
            <p className="text-sm text-gray-300">Телефон: +7 495 123-45-67</p>
            <p className="text-sm text-gray-300">Москва, Россия</p>
          </div>
        </div>

        <div className="border-t border-gray-700 mt-8 pt-8 text-center">
          <p className="text-sm text-gray-400">
            &copy; 2025 ChatBot AI. Все права защищены.
          </p>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
