class MainHeader extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback() {
        this.render();
        this.initSidebar();
    }

    render() {
        this.innerHTML = `
        <header class="main-header">
            <div class="header-container">
                <button class="sidebar-toggle" id="openSidebar" aria-label="Открыть меню">
                    <span></span>
                    <span></span>
                    <span></span>
                </button>

                <a href="/login" class="profile-btn">
                    <img src="/static/Person.png" alt="Профиль" class="profile-img">
                </a>
            </div>
        </header>

        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <h3>GETCASE</h3>
                <button class="close-btn" id="closeSidebar">&times;</button>
            </div>
            <nav class="sidebar-nav">
                <ul>
                    <li><a href="#">ПРОФИЛЬ</a></li>
                    <li><a href="#">КЕЙСЫ В РАБОТЕ</a></li>
                    <li><a href="#">ВСЕ КЕЙСЫ</a></li>
                    <li><hr></li>
                    <li><a href="#">ВЫЙТИ ИЗ ПРОФИЛЯ</a></li>
                </ul>
            </nav>
        </aside>
        <div class="overlay" id="overlay"></div>

        <style>
            :root {
                --primary-color: #6f2c80;
                --accent-color: #b023d3;
                --text-color: #000000;
                --bg-color: #EBE9E9;
                --sidebar-width: 20%;
            }
            body {
                margin: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: var(--bg-color);
                color: var(--text-color);
            }
            .main-header {
                background-color: transparent;
                padding: 1rem 0;
                position: absolute;
                top: 0;
                width: 100%;
                z-index: 100;
            }
            .header-container {
                display: flex;
                justify-content: space-between;
                align-items: center;
                max-width: 97%;
                margin: 0 auto;
                padding: 0 20px;
            }
            .sidebar-toggle {
                background: none;
                border: none;
                cursor: pointer;
                display: flex;
                flex-direction: column;
                gap: 5px;
                margin-top: 20px;
            }
            .sidebar-toggle span {
                display: block;
                width: 25px;
                height: 3px;
                background-color: white;
                border-radius: 2px;
            }
            .sidebar {
                position: fixed;
                top: 0;
                left: -300px;
                width: 300px;
                height: 100%;
                background: white;
                z-index: 1000;
                transition: 0.3s ease;
                box-shadow: 2px 0 10px rgba(0,0,0,0.2);
            }
            .sidebar.active { left: 0; }
            .sidebar-header {
                padding: 20px;
                background: #6f2c80;
                color: white;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .close-btn { background: none; border: none; color: white; font-size: 2rem; cursor: pointer; }
            .sidebar-nav ul { list-style: none; padding: 20px; }
            .sidebar-nav li { margin-bottom: 15px; }
            .sidebar-nav a { text-decoration: none; color: black; font-weight: 500; }
            .sidebar-nav a:hover { color: #b023d3; }
            .overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                display: none;
                z-index: 999;
            }
            .overlay.active { display: block; }
            .profile-btn {
                width: 44px;
                height: 44px;
                background: rgba(255,255,255,0.18);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 1px solid rgba(255,255,255,0.25);
                transition: 0.2s;
                overflow: hidden;
                margin-top: 20px;
            }
            .profile-img { width: 100%; height: 100%; object-fit: cover; }
        </style>
        `;
    }

    initSidebar() {
        const openBtn = this.querySelector('#openSidebar');
        const closeBtn = this.querySelector('#closeSidebar');
        const sidebar = this.querySelector('#sidebar');
        const overlay = this.querySelector('#overlay');

        const toggle = () => {
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        };

        openBtn.addEventListener('click', toggle);
        closeBtn.addEventListener('click', toggle);
        overlay.addEventListener('click', toggle);
    }
}

// Регистрируем наш тег
customElements.define('main-header', MainHeader);