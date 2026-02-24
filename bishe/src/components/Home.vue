<template>
  <div class="home-container">
    <!-- 侧边栏 -->
    <div class="sidebar">
      <div class="logo">学生画像分析系统</div>
      <ul class="nav-menu">
        <li class="nav-item" :class="{ active: currentView === 'dashboard' }" @click="currentView = 'dashboard'">
          <span class="icon"><svg t="1771900009109" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="7494" width="50" height="50"><path d="M513.5 1021.2c-68.7 0-135.3-13.5-198-40-60.6-25.6-115-62.3-161.7-109s-83.4-101.1-109-161.7c-26.5-62.7-40-129.3-40-198s13.5-135.3 40-198c25.6-60.6 62.3-115 109-161.7S255 69.6 315.5 44c62.7-26.5 129.3-40 198-40s135.3 13.5 198 40c60.6 25.6 115 62.3 161.7 109s83.4 101.1 109 161.7c26.5 62.7 40 129.3 40 198s-13.5 135.3-40 198c-25.6 60.6-62.3 115-109 161.7s-101.1 83.4-161.7 109c-62.7 26.3-129.4 39.8-198 39.8z m0-969.2c-254 0-460.6 206.6-460.6 460.6s206.6 460.6 460.6 460.6 460.6-206.6 460.6-460.6S767.5 52 513.5 52z" p-id="7495" fill="#ffffff"></path><path d="M514 912.1l-0.1-48c14.7 0 29.6-1 44.1-2.8l6 47.6c-16.5 2.1-33.3 3.2-50 3.2z m-50.1-3.1c-16.6-2.1-33.2-5.2-49.3-9.3l11.8-46.5c14.2 3.6 28.8 6.4 43.4 8.2l-5.9 47.6z m149.4-9.5l-12-46.5c14.2-3.7 28.3-8.2 41.9-13.7L661 884c-15.5 6.1-31.6 11.4-47.7 15.5z m-246.5-15.2c-15.5-6.1-30.8-13.3-45.4-21.3l23.1-42.1c12.9 7.1 26.3 13.4 39.9 18.8l-17.6 44.6z m339.5-21.8l-23.2-42c12.8-7.1 25.3-15.1 37.2-23.7l28.3 38.8c-13.5 9.8-27.7 18.9-42.3 26.9zM279 836.1c-13.5-9.8-26.5-20.5-38.7-31.9l32.8-35c10.7 10 22.2 19.5 34 28.1L279 836.1z m508.2-32.5l-32.9-35c10.7-10.1 20.9-20.9 30.2-32.2l37 30.6c-10.6 12.9-22.2 25.2-34.3 36.6z m-581.2-36c-10.7-12.8-20.6-26.5-29.6-40.5l40.5-25.8c7.9 12.4 16.6 24.3 26 35.6L206 767.6z m645-41.1l-40.5-25.7c7.9-12.4 15-25.4 21.3-38.7l43.4 20.4c-7.1 15.1-15.3 29.9-24.2 44z m-698.8-43.2c-7.1-15.1-13.4-30.8-18.6-46.6l45.6-14.9c4.5 13.9 10 27.7 16.3 41l-43.3 20.5z m741.4-47.5L848 621c4.5-13.9 8.2-28.3 10.9-42.7l47.2 8.9c-3.2 16.4-7.3 32.7-12.5 48.6zM121.1 588c-3.1-16.3-5.2-33.1-6.3-49.8l47.9-3c0.9 14.7 2.8 29.4 5.5 43.8l-47.1 9z m791.1-50.6l-47.9-2.9c0.4-7.2 0.7-14.6 0.7-21.9 0-7.4-0.2-14.9-0.7-22.3l47.9-3c0.5 8.4 0.8 16.9 0.8 25.3 0 8.2-0.3 16.6-0.8 24.8z m-749.6-46.3l-47.9-2.9c1-16.7 3.1-33.4 6.1-49.8l47.2 8.9c-2.7 14.4-4.5 29.1-5.4 43.8z m696.2-44.6c-2.7-14.4-6.4-28.8-11-42.7l45.6-14.8c5.2 15.9 9.3 32.2 12.5 48.6l-47.1 8.9z m-679.9-42l-45.7-14.7c5.1-15.9 11.3-31.6 18.4-46.7l43.5 20.4c-6.2 13.3-11.7 27.1-16.2 41z m652.7-41.7c-6.3-13.2-13.4-26.2-21.3-38.6l40.5-25.8c9 14.1 17.1 28.8 24.2 43.9l-43.4 20.5z m-615.3-38l-40.6-25.7c8.9-14.1 18.8-27.7 29.4-40.6l37 30.5c-9.2 11.3-17.9 23.4-25.8 35.8z m568-36.3c-9.4-11.3-19.5-22.1-30.2-32.2l32.9-35c12.2 11.4 23.7 23.7 34.3 36.5l-37 30.7z m-511.9-31.7l-32.9-34.9c12.1-11.4 25.1-22.2 38.6-32l28.3 38.8c-11.9 8.5-23.3 18-34 28.1z m447.7-28.7c-11.9-8.6-24.4-16.6-37.3-23.7l23.2-42c14.6 8 28.8 17.1 42.3 26.9l-28.2 38.8z m-376.6-23.3l-23.2-42c14.6-8.1 29.8-15.3 45.3-21.5l17.8 44.6c-13.6 5.5-27 11.8-39.9 18.9z m299.4-19.2c-13.6-5.4-27.8-10-42-13.6l11.9-46.5c16.2 4.1 32.2 9.4 47.8 15.5l-17.7 44.6z m-217.6-13.4l-12-46.5c16.1-4.2 32.7-7.3 49.3-9.5l6.1 47.6c-14.6 2-29.2 4.8-43.4 8.4z m132.3-8.4c-14.5-1.8-29.3-2.7-44.1-2.7h-0.8l-0.2-48h0.9c16.7 0 33.5 1 50 3.1l-5.8 47.6z" p-id="7496" fill="#ffffff"></path><path d="M519.8 512.6c-69.5 0-209.1 34.3-209.1 102.3v111.2c0 6.2 5.3 11.2 11.8 11.2h394.6c6.5 0 11.8-5.1 11.8-11.2V614.9c0-68-139.6-102.3-209.1-102.3z m-8.3-45.5c61.8 7.3 113.1-42.7 104.8-101.1-5.3-40.5-39.5-72.5-81.3-77.5-61.8-7.3-113.7 42.1-105.4 101.1 6 40.5 39.5 72.5 81.9 77.5z" p-id="7497" fill="#ffffff"></path></svg></span>
          <span class="text">查看画像</span>
        </li>
        <li class="nav-item" :class="{ active: currentView === 'userProfile' }" @click="currentView = 'userProfile'">
          <span class="icon"><svg t="1769478201122" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="6107" width="50" height="50"><path d="M639.984002 1024v-127.984002h383.952006v127.984002z m-639.92001-63.992001v-95.988001a288.731909 288.731909 0 0 1 287.964005-287.964005H512v127.984002H288.027997a159.980002 159.980002 0 0 0-159.980003 159.980003v95.988001a63.992001 63.992001 0 1 1-127.984002 0z m639.92001-127.984002v-127.984002h383.952006v127.984002z m0-191.976003v-127.984002h383.952006v127.984002z m-447.944007-383.952006a255.968004 255.968004 0 1 1 255.968004 255.968004 255.968004 255.968004 0 0 1-255.968004-255.968004z m127.984002 0a127.984002 127.984002 0 1 0 127.984002-127.984002 127.984002 127.984002 0 0 0-127.984002 127.984002z" fill="#b2b4b7" p-id="6108"></path></svg></span>
          <span class="text">个人信息管理</span>
        </li>
        <li class="nav-item" :class="{ active: currentView === 'survey' }" @click="currentView = 'survey'">
          <span class="icon"><svg t="1769481345592" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="18426" width="50" height="50"><path d="M853.333333 853.333333H170.666667V170.666667h341.333333v-85.333334H170.666667c-47.36 0-85.333333 37.973333-85.333334 85.333334v682.666666c0 47.36 37.973333 85.333333 85.333334 85.333334h682.666666c47.36 0 85.333333-37.973333 85.333334-85.333334v-341.333333h-85.333334v341.333333zM426.666667 640l213.333333-213.333333 128 128L554.666667 768H426.666667v-128z m462.933333-322.133333l-61.866667 61.866666-128-128 61.866667-61.866666c17.066667-17.066667 44.8-17.066667 61.866667 0l66.133333 66.133333c17.066667 17.066667 17.066667 44.8 0 61.866667z" fill="#b2b4b7" p-id="18427"></path></svg></span>
          <span class="text">问卷填写</span>
        </li>
        <li class="nav-item" v-if="userRole === 'admin'" :class="{ active: isConfigOpen || ['userManagement', 'dataImport', 'questionnaireConfig'].includes(currentView) }" @click="toggleConfig">
          <span class="icon"><svg t="1769481345592" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="18426" width="50" height="50"><path d="M920.463 444.9l-0.138-0.032-16.609-3.8-1.45-0.439c-47.211-14.281-87.326-45.521-112.538-89.067-25.243-43.822-32.297-94.819-20.685-142.938l0.438-1.815 4.999-15.004 0.029-0.212c0.053-0.431 0.08-0.98 0.063-1.62-0.04-1.632-0.341-3.524-0.896-5.428-0.556-1.904-1.32-3.661-2.164-5.058-0.479-0.793-0.876-1.304-1.068-1.512-0.27-0.213-0.62-0.484-1.052-0.812-1.894-1.44-4.414-3.262-7.605-5.46-9.708-6.686-22.649-14.821-39.183-24.365-16.599-9.504-30.148-16.644-40.806-21.739-3.517-1.682-6.373-2.973-8.587-3.915a84.987 84.987 0 0 0-1.22-0.51l-0.177-0.032a10.37 10.37 0 0 0-1.52-0.134c-1.568-0.037-3.415 0.17-5.298 0.628-1.903 0.463-3.683 1.144-5.125 1.928-0.994 0.541-1.599 0.998-1.707 1.113l-11.491 12.275-0.97 0.918c-35.84 33.906-83.166 53.06-133.615 53.06-50.536 0-98.273-19.408-134.09-53.538l-0.929-0.884-11.083-11.868-0.097-0.105c-2.026-2.182-10.684-4.312-13.607-3.406-0.357 0.142-0.842 0.34-1.457 0.6-2.223 0.94-5.089 2.227-8.614 3.905-10.674 5.078-24.209 12.194-40.754 21.665-16.492 9.6-29.368 17.764-39 24.459-3.163 2.199-5.655 4.018-7.522 5.452a63.609 63.609 0 0 0-1.219 0.954l-0.126 0.106c0.04-0.034-0.014 0.02-0.139 0.17-0.258 0.308-0.557 0.725-0.871 1.241-0.812 1.332-1.55 3.021-2.091 4.866-0.546 1.862-0.843 3.726-0.883 5.349-0.028 1.116 0.064 1.857 0.123 2.052l4.77 15.72 0.317 1.341c11.385 48.205 4.416 98.895-20.738 142.546-25.209 43.782-65.804 75.28-113.35 89.333l-1.39 0.41-1.414 0.319-14.493 3.264c-2.887 0.656-9.097 7.094-9.81 10.131-0.053 0.357-0.12 0.84-0.198 1.454-0.297 2.353-0.613 5.437-0.918 9.291-0.932 11.744-1.505 27.03-1.505 46.158 0 19.12 0.573 34.402 1.505 46.143 0.305 3.853 0.62 6.937 0.918 9.29 0.082 0.645 0.151 1.146 0.205 1.506 0.679 3.036 6.796 9.404 9.69 10.054l0.13 0.029 15.642 3.614 1.275 0.377c47.657 14.093 88.39 45.656 113.55 89.546 25.224 43.817 32.268 94.79 20.668 142.894l-0.276 1.146-4.57 15.3-0.04 0.132c0.012-0.04-0.008 0.056-0.035 0.275-0.054 0.431-0.08 0.98-0.064 1.622 0.04 1.632 0.342 3.525 0.897 5.43 0.556 1.904 1.319 3.66 2.162 5.056 0.478 0.79 0.873 1.298 1.062 1.503 0.272 0.215 0.623 0.487 1.057 0.817 1.898 1.442 4.42 3.265 7.612 5.464 9.725 6.7 22.686 14.85 39.234 24.408 16.569 9.563 30.07 16.694 40.667 21.734 3.472 1.652 6.282 2.91 8.447 3.817 0.583 0.245 1.039 0.43 1.369 0.56 0.024 0.003 0.103 0.02 0.235 0.043 0.402 0.071 0.92 0.121 1.531 0.136 1.574 0.037 3.424-0.17 5.31-0.63 1.902-0.462 3.681-1.143 5.122-1.927 0.97-0.527 1.568-0.974 1.746-1.156l10.878-11.66 0.995-0.942c36.046-34.116 83.559-53.428 134.166-53.428 50.63 0 98.385 19.513 134.28 53.728l0.929 0.886 10.907 11.683 0.099 0.107c2.02 2.178 10.668 4.304 13.619 3.39 0.356-0.141 0.839-0.339 1.451-0.597 2.222-0.937 5.085-2.224 8.608-3.9 10.687-5.082 24.241-12.21 40.813-21.704 16.5-9.52 29.373-17.631 38.992-24.294 3.15-2.182 5.628-3.986 7.481-5.408a61.231 61.231 0 0 0 1.2-0.94l0.127-0.106c-0.056 0.047-0.013 0.004 0.104-0.136 0.256-0.306 0.554-0.724 0.87-1.243 0.818-1.348 1.566-3.065 2.113-4.942 0.554-1.898 0.856-3.799 0.897-5.454 0.028-1.136-0.065-1.887-0.13-2.104l-0.033-0.105-4.746-15.818-0.297-1.252c-11.41-48.075-4.416-98.805 20.733-142.242 25.221-43.775 65.994-75.444 113.51-89.51l1.284-0.38 15.529-3.585 0.174-0.04c2.864-0.65 9.072-7.086 9.783-10.111 0.053-0.357 0.12-0.84 0.197-1.455 0.297-2.353 0.612-5.437 0.917-9.291 0.928-11.725 1.501-26.981 1.501-46.068-0.075-18.724-0.67-33.802-1.594-45.511-0.327-4.144-0.665-7.464-0.985-10.001a75.83 75.83 0 0 0-0.222-1.641c-0.71-3.022-6.91-9.488-9.736-10.125zM301.325 147.374l0.263-0.152a919.447 919.447 0 0 0-0.263 0.152z m715.51 292.188v0.006c0.702 3.893 1.535 10.502 2.299 20.174 1.103 13.977 1.783 31.27 1.866 52.175v0.173c0 21.385-0.658 38.98-1.776 53.1-0.726 9.166-1.521 15.466-2.186 19.164-6.741 37.758-39.578 72.042-76.88 80.546l-12.738 2.942c-25.59 7.891-47.443 25.063-61.112 48.786-13.579 23.454-17.48 50.66-11.58 76.76l3.962 13.207c11.059 36.626-2.127 81.928-31.366 106.591-2.97 2.527-7.996 6.372-15.43 11.521-11.679 8.09-26.614 17.5-45.184 28.212l-0.111 0.064c-18.492 10.595-34.042 18.773-46.819 24.85-4.693 2.232-8.753 4.056-12.201 5.51-2.367 1-4.163 1.706-5.389 2.153-36.096 13.165-82.24 1.975-108.353-26.124l-9.04-9.684c-19.587-18.268-45.319-28.621-72.709-28.621-27.45 0-53.018 10.221-72.76 28.484l-9.019 9.668-0.1 0.106c-26.234 27.938-72.053 39.106-108.096 26.04-3.6-1.297-9.415-3.738-17.622-7.642-12.764-6.071-28.322-14.289-46.87-24.993-18.528-10.702-33.458-20.09-45.155-28.149-7.59-5.228-12.661-9.083-15.578-11.55l-0.084-0.07c-29.15-24.781-42.39-70.066-31.315-106.57l3.794-12.704c6.008-26.06 2.073-53.514-11.648-77.335l-0.051-0.09c-13.536-23.625-35.285-40.677-61.007-48.595l-12.704-2.935c-37.462-8.49-70.17-42.754-76.891-80.488-0.676-3.752-1.474-10.055-2.202-19.224C3.66 550.897 3 533.3 3 511.915c0-21.391 0.66-38.993 1.78-53.12 0.728-9.17 1.526-15.474 2.187-19.146 6.734-37.783 39.615-72.085 77.038-80.597l13.052-2.94c25.558-7.893 47.178-24.88 60.767-48.481 13.621-23.638 17.526-50.878 11.632-77.162l-3.945-13c-11.091-36.648 2.097-81.808 31.359-106.48 2.943-2.503 7.945-6.335 15.36-11.489 11.652-8.1 26.56-17.55 45.1-28.338l0.132-0.077 0.132-0.075c18.491-10.59 34.037-18.764 46.808-24.84 4.69-2.231 8.746-4.055 12.19-5.51 2.364-0.997 4.156-1.704 5.402-2.158 36.091-13.164 82.233-1.97 108.346 26.116l9.217 9.87c19.477 18.154 45.177 28.443 72.531 28.443 27.351 0 52.733-10.106 72.244-28.151l9.642-10.3c26.265-27.955 72.15-39.122 108.197-25.98l0.145 0.053c1.227 0.452 3 1.157 5.34 2.153 3.413 1.452 7.438 3.271 12.097 5.499 12.69 6.066 28.18 14.23 46.647 24.805l0.128 0.074c18.539 10.7 33.475 20.088 45.176 28.147 7.593 5.23 12.668 9.088 15.588 11.559l0.084 0.071c29.184 24.824 42.417 70.19 31.258 106.717l-0.161 0.528-4.273 12.824c-5.81 25.872-1.83 53.079 11.733 76.622 13.608 23.504 34.99 40.375 60.485 48.436l13.475 3.083c37.41 8.47 70.156 42.846 76.941 80.492zM512.5 716C400.168 716 309 624.855 309 512.428 309 400.073 400.087 309 512.5 309 624.837 309 716 400.149 716 512.66 715.797 624.966 624.746 716 512.5 716z m0-88c63.675 0 115.385-51.7 115.5-115.42C628 448.753 576.239 397 512.5 397 448.685 397 397 448.677 397 512.428 397 576.249 448.764 628 512.5 628z" fill="#ffffff" p-id="18427"></path></svg></span>
          <span class="text">配置管理</span>
        </li>
        <ul v-show="isConfigOpen && userRole === 'admin'" class="sub-menu">
          <li class="sub-menu-item" :class="{ active: currentView === 'userManagement' }" @click.stop="currentView = 'userManagement'">用户管理</li>
          <li class="sub-menu-item" :class="{ active: currentView === 'questionnaireConfig' }" @click.stop="currentView = 'questionnaireConfig'">问卷配置</li>
          <li class="sub-menu-item" :class="{ active: currentView === 'dataImport' }" @click.stop="currentView = 'dataImport'">数据导入</li>
        </ul>
      </ul>
      <div class="nav-item logout" @click="handleLogout">
        <span class="icon"><svg t="1769478261066" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="8386" width="50" height="50"><path d="M936.96 25.6H364.032c-28.16 0-51.2 23.04-51.2 51.2s23.04 51.2 51.2 51.2H885.76v768H364.032c-28.16 0-51.2 23.04-51.2 51.2s23.04 51.2 51.2 51.2H936.96c28.16 0 51.2-23.04 51.2-51.2v-870.4c0-28.16-23.04-51.2-51.2-51.2z" fill="#b2b4b7" p-id="8387"></path><path d="M316.416 667.648L210.944 563.2h395.264c28.16 0 51.2-23.04 51.2-51.2s-23.04-51.2-51.2-51.2H211.456l104.96-103.936c19.968-19.968 20.48-52.224 0.512-72.192-19.968-20.48-52.224-20.48-72.704-1.024L51.2 475.136c-9.728 9.728-15.36 22.528-15.36 36.352s5.632 26.624 15.36 36.352l193.536 192a51.2512 51.2512 0 0 0 72.192 0 50.9952 50.9952 0 0 0-0.512-72.192z" fill="#b2b4b7" p-id="8388"></path></svg></span>
        <span class="text">退出</span>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="main-content">
      <!-- 头部 -->
      <div class="header">
        <div class="header-left">{{ currentTime }}</div>
        <div class="header-right">
          <div class="avatar-circle">
            <span v-if="userRole === 'student'" class="avatar-icon"><svg t="1769478920157" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="9672" width="20" height="20"><path d="M500 658.7c-3.9 0-7.7-1-11.2-3L76.5 415.6c-6.9-4-11.1-11.5-11-19.5 0.1-8 4.5-15.3 11.5-19.2l436.4-240.1c6.8-3.8 15.1-3.7 21.9 0.3l412.4 240c6.9 4 11.1 11.5 11 19.5-0.1 8-4.5 15.3-11.5 19.2L510.7 655.9c-3.3 1.9-7 2.8-10.7 2.8zM132.8 397l367.6 214 390.9-215.1-367.6-214L132.8 397z" fill="#ffffff" p-id="9673"></path><path d="M869.038 424.736l44.5-0.424 2.404 252.3-44.5 0.424zM515.3 889.9C350.8 889.9 217 756.1 217 591.6V487.5h44.5v104.1c0 140 113.9 253.8 253.8 253.8s253.8-113.9 253.8-253.8V470.5h44.5v121.1c0 164.5-133.8 298.3-298.3 298.3z" fill="#ffffff" p-id="9674"></path></svg></span>
            <span v-if="userRole === 'teacher'" class="avatar-icon"><svg t="1769478950720" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="11098" width="20" height="20"><path d="M311.6 592.8c-80.4 0-145.7-65.4-145.7-145.7s65.4-145.7 145.7-145.7S457.3 366.7 457.3 447s-65.4 145.8-145.7 145.8z m0-243.6c-53.9 0-97.8 43.9-97.8 97.8s43.9 97.8 97.8 97.8 97.8-43.9 97.8-97.8-43.9-97.8-97.8-97.8zM556.5 902.6h-47.9V758.3c0-56.4-45.9-102.3-102.3-102.3H216.8c-56.4 0-102.3 45.9-102.3 102.3v144.3H66.6V758.3C66.6 675.4 134 608 216.8 608h189.4c82.8 0 150.2 67.4 150.2 150.2v144.4z" fill="#ffffff" p-id="11099"></path><path d="M957.4 798.7H657.8v-47.9h251.7V159.5H272.4v107.9h-47.9V111.6h732.9z" fill="#ffffff" p-id="11100"></path><path d="M510.715 892.736l184.668-411.903 43.709 19.596-184.668 411.903z" fill="#ffffff" p-id="11101"></path></svg></span>
            <span v-if="userRole === 'admin'" class="avatar-icon"><svg t="1770006886227" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="7785" width="20" height="20"><path d="M956.96497373 783.22135977c-3.28732207 17.50931455-14.60263008 28.85922598-28.7208123 28.85922598h-2.35303067c-27.68271065 0.06920684-50.10570703 22.49220234-50.17491299 50.17491386 0.3806376 6.57464414 1.90318623 13.04547715 4.42923311 19.10107002 6.74766035 15.70993857 1.59175547 33.94592402-12.35340967 43.80789024l-1.38413496 0.9342914-58.23750322 32.04273779a37.37165977 37.37165977 0 0 1-15.9521625 3.66795967c-10.93467041 0-21.73092803-4.60225107-28.58239863-12.24960029-7.50893555-8.13179619-27.37128076-24.94904326-41.35104932-24.94904238-13.66833867 0-33.87671719 16.81724707-40.93580919 24.49919883a39.34405283 39.34405283 0 0 1-43.1850287 8.96227733l-57.58003828-32.00813437c-15.15628388-10.51943028-20.45060244-29.41288066-13.56452842-44.77678506 1.21111875-2.83747763 4.39463057-11.83435927 4.39463056-18.96265635 0-27.64810722-22.5960126-50.17491387-50.2441207-50.17491386h-1.97239306c-14.46421641 0-25.71031758-11.38451484-29.06684649-28.92843281-0.51905039-2.66446055-4.94828438-26.99064316-4.94828437-46.5069542 0-19.58551787 4.42923398-43.98090732 4.94828437-46.57616104 3.35652891-17.50931455 14.60263008-28.92843281 28.7208123-28.92843281h2.35303067c27.68271065 0 50.17491387-22.38839209 50.24412071-50.07110362a56.40352383 56.40352383 0 0 0-4.46383741-19.17027685 36.26435127 36.26435127 0 0 1 12.4226165-43.84249365l1.38413584-0.83048116 59.69084502-32.80401211 1.14191192-0.44984443a39.69008701 39.69008701 0 0 1 42.80439111 8.92767393c7.26671162 7.6127458 26.81762607 23.49570059 40.34755195 23.49570146 13.32230449 0 32.76940869-15.53692148 40.03612031-23.11506386 11.31530801-11.17689434 28.20176192-14.53342325 42.90820137-8.54703721l58.61814082 32.42337539c15.22549073 10.51943028 20.5544127 29.4820875 13.63373526 44.8459919a59.06798438 59.06798438 0 0 0-4.32542373 18.99725976c0.06920684 27.64810722 22.49220234 50.0365002 50.17491299 50.07110362h2.00699648c14.42961299 0 25.71031758 11.38451484 29.06684649 28.96303623 0.48444785 2.62985713 4.94828438 26.95603974 4.94828524 46.57616102 0 20.58901612-4.94828438 46.33393711-4.87907841 46.54155763z m-43.70407998-77.30396983a95.74757666 95.74757666 0 0 1-83.29035586-94.88249209c0.17301709-9.89656875 1.90318623-19.65472471 5.12130146-28.99763965l-41.48946299-23.04585615a170.87153291 170.87153291 0 0 1-17.12867695 13.84135488c-18.1321752 12.73404727-35.43387011 19.17027685-51.6974625 19.17027774-16.50581631 0-34.01513086-6.43623047-52.21651376-19.51631103a149.83267237 149.83267237 0 0 1-17.16328038-14.22199336l-43.39265009 23.84173476c2.4222375 7.19750479 5.15590488 17.82074531 5.15590488 28.96303623a95.85138604 95.85138604 0 0 1-83.35956269 94.95169893 226.82521231 226.82521231 0 0 0-2.87208106 30.65860195c0.27682734 10.24260292 1.21111875 20.45060244 2.87208106 30.58939512a95.71297324 95.71297324 0 0 1 83.35956269 94.95169892c0 11.07308408-2.83747763 21.76553144-5.19050831 28.99763965l40.13993145 22.42299551c5.43273223-5.1905083 11.14229092-10.03498242 17.16328037-14.49881982 18.40900253-13.42611474 36.29895469-20.34679219 52.97778809-20.34679219 16.92105732 0 34.94942227 7.05909112 53.53144189 20.79663662 6.05559287 4.53304424 11.83435927 9.48132862 17.26709151 14.77564628l42.00851338-23.1496664a95.02090489 95.02090489 0 0 1-5.08669805-28.96303623 95.67836982 95.67836982 0 0 1 83.29035586-94.95169893c1.17651533-7.92417568 2.87208106-20.72742979 2.87208193-30.69320537 0-10.00037901-1.69556573-22.73442627-2.87208193-30.69320537z m-190.73387724 118.9664499a88.75769151 88.75769151 0 0 1-88.61927872-88.58467529 88.65388125 88.65388125 0 0 1 177.23855655 0 88.75769151 88.75769151 0 0 1-88.61927783 88.58467529z m0-129.76270752c-23.04585703 0-42.00851338 18.20138203-42.97740909 41.21263565a42.9774082 42.9774082 0 0 0 85.92021387 0 43.01201162 43.01201162 0 0 0-42.94280478-41.21263565z m-128.58619219-225.61409355l-14.42961299 11.21149776c-29.37827724 26.12555859-85.43576602 34.84561201-122.4959959 37.71769394l-4.74066387-0.10381026a344.64975029 344.64975029 0 0 0-31.21225664 1.48794522h-0.44984443l0.06920683 0.06920684c-167.65341768 15.81374883-299.28470801 156.30350625-299.284708 326.93281611v50.14030957h367.38417656a298.76565674 298.76565674 0 0 0 35.81450771 58.61814082H91.77644902A29.4820875 29.4820875 0 0 1 62.15594785 926.30637178v-79.4839834c0-159.10638047 96.47424756-300.18439599 245.85707637-359.42539746l16.92105732-6.6784544-14.36040615-11.21149775c-56.12669648-43.77328682-88.23864112-109.06988115-88.23864112-179.31475986 0-125.74871455 103.11809766-228.03633106 229.87031046-228.03633106 126.78681622 0 229.90491386 102.28761651 229.9741207 228.03633106 0 70.24487871-32.2503583 135.54147305-88.23864111 179.31475986zM452.23994815 120.80869209c-94.08661347 0-170.62930898 76.02364511-170.62930899 169.38358682 0 93.42914941 76.5426955 169.45279365 170.62930899 169.45279453 94.1212169 0 170.6639124-75.9890417 170.6639124-169.45279453 0-93.42914941-76.5426955-169.38358682-170.6639124-169.38358682z" p-id="7786" fill="#ffffff"></path></svg></span>
            <span v-if="!userRole" class="avatar-icon"><svg t="1769478993164" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="13468" width="20" height="20"><path d="M512.02048 476.09856c-84.3776 0-153.00608-68.62848-153.00608-152.9856s68.62848-152.9856 153.00608-152.9856c84.35712 0 152.9856 68.62848 152.9856 152.9856s-68.62848 152.9856-152.9856 152.9856z m0-260.93568c-59.53536 0-107.97056 48.4352-107.97056 107.95008s48.4352 107.95008 107.97056 107.95008c59.51488 0 107.95008-48.4352 107.95008-107.95008s-48.4352-107.95008-107.95008-107.95008zM623.63648 853.85216H400.384c-105.49248 0-191.32416-76.20608-191.32416-169.86112 0-93.63456 85.83168-169.84064 191.32416-169.84064h223.25248c105.472 0 191.32416 76.20608 191.32416 169.84064 0 93.67552-85.83168 169.86112-191.32416 169.86112zM400.384 559.18592c-80.67072 0-146.30912 55.99232-146.30912 124.8256 0 68.83328 65.6384 124.84608 146.30912 124.84608h223.25248c80.65024 0 146.30912-55.99232 146.30912-124.84608 0-68.8128-65.6384-124.8256-146.30912-124.8256H400.384z" fill="#ffffff" p-id="13469"></path></svg></span>
          </div>
          <span class="username">{{ username }}</span>
        </div>
      </div>

      <!-- 内容区域 -->
      <div class="content-wrapper">
        <!-- 仪表盘内容 -->
        <div v-if="currentView === 'dashboard'" class="dashboard-content">
          <div class="dashboard-header">
            <div style="display: flex; align-items: center;">
              <div class="dashboard-title">画像查看</div>
              <button
                v-if="currentDimension === 'student'"
                @click="generateTags"
                class="generate-btn"
                :disabled="loadingTags"
                style="margin-left: 15px;"
              >
                {{ loadingTags ? '生成中...' : '生成/更新标签' }}
              </button>
            </div>
            <div class="dimension-selector">
              <span class="dimension-label">维度：</span>
              <div class="btn-group">
                <button
                  v-for="(label, key) in dimensionMap"
                  :key="key"
                  :class="['dim-btn', { active: currentDimension === key }]"
                  @click="currentDimension = key"
                >
                  {{ label }}
                </button>
              </div>
            </div>
          </div>

          <!-- 图表区域占位符 -->
          <div class="container">
            <!-- 图表区域 -->
            <div class="dimension-content">
              <div v-if="currentDimension === 'student'" class="student-tags-container">
                <div v-if="tags.length === 0" class="no-tags">
                  暂无标签数据，请点击生成按钮获取最新画像。
                </div>

                <div class="tags-grid">
                  <div v-for="tag in tags" :key="tag.tag_name" class="tag-card" :class="getTagClass(tag)">
                    <div class="tag-header-row">
                      <span class="tag-name">{{ tag.tag_name }}</span>
                      <div class="info-icon-wrapper" :title="tag.description">
                        <svg t="1771899969833" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="5242" width="20" height="20"><path d="M518.542222 284.444444a145.066667 145.066667 0 0 0-108.373333 40.106667A144.213333 144.213333 0 0 0 369.777778 431.786667h66.275555a105.813333 105.813333 0 0 1 16.782223-64.568889A70.257778 70.257778 0 0 1 514.844444 341.333333a71.111111 71.111111 0 0 1 52.622223 18.773334 72.248889 72.248889 0 0 1 18.204444 51.2 73.955556 73.955556 0 0 1-16.782222 45.511111l-10.524445 11.946666a343.324444 343.324444 0 0 0-71.395555 77.653334 132.266667 132.266667 0 0 0-11.946667 59.448889v10.524444H540.444444v-10.524444a85.333333 85.333333 0 0 1 9.955556-41.813334 108.657778 108.657778 0 0 1 25.6-31.857777A611.84 611.84 0 0 0 630.613333 483.555556a123.164444 123.164444 0 0 0 23.608889-76.8 113.777778 113.777778 0 0 0-36.977778-89.6A142.222222 142.222222 0 0 0 518.542222 284.444444z m-10.524444 366.08a41.813333 41.813333 0 0 0-31.857778 12.515556 40.106667 40.106667 0 0 0-13.653333 31.857778 46.08 46.08 0 0 0 45.511111 44.657778 48.924444 48.924444 0 0 0 32.426666-12.231112 44.088889 44.088889 0 0 0 13.084445-32.426666A40.96 40.96 0 0 0 540.444444 662.755556a44.942222 44.942222 0 0 0-33.28-12.515556z" p-id="5243" fill="#cdcdcd"></path><path d="M512 56.888889A455.111111 455.111111 0 1 1 56.888889 512 455.111111 455.111111 0 0 1 512 56.888889m0-56.888889a512 512 0 1 0 512 512A512 512 0 0 0 512 0z" p-id="5244" fill="#cdcdcd"></path></svg>
                      </div>
                    </div>
                    <div class="tag-value">{{ formatValue(tag.tag_value) }}</div>
                  </div>
                </div>
              </div>
              <div v-else class="dimension-placeholder">
                {{ dimensionMap[currentDimension] }}
              </div>
            </div>
          </div>
        </div>

        <!-- 用户信息占位符 -->
        <UserProfile v-if="currentView === 'userProfile'" />

        <!-- 用户管理 -->
        <UserManagement v-if="currentView === 'userManagement' && userRole === 'admin'" />

        <!-- 问卷配置 -->
        <QuestionnaireConfig v-if="currentView === 'questionnaireConfig' && userRole === 'admin'" />

        <!-- 数据导入 -->
        <DataImport v-if="currentView === 'dataImport' && userRole === 'admin'" />

        <!-- 问卷填写 -->
        <Survey v-if="currentView === 'survey'" />
      </div>
    </div>

    <!-- 退出确认弹窗 -->
    <div v-if="showLogoutModal" class="modal-overlay">
      <div class="modal-content">
        <h3>确认退出</h3>
        <p>您确定要退出登录吗？</p>
        <div class="modal-actions">
          <button class="modal-btn cancel" @click="cancelLogout">取消</button>
          <button class="modal-btn confirm-logout" @click="confirmLogout">确认退出</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import UserProfile from './UserProfile'
import UserManagement from './UserManagement'
import DataImport from './DataImport'
import Survey from './Survey'
import QuestionnaireConfig from './QuestionnaireConfig'

export default {
  name: 'Home',
  components: {
    UserProfile,
    UserManagement,
    DataImport,
    Survey,
    QuestionnaireConfig
  },
  data () {
    return {
      currentView: 'dashboard',
      currentTime: '',
      timer: null,
      userRole: '',

      username: '',
      isConfigOpen: false,
      showLogoutModal: false,
      currentDimension: 'student',
      dimensionMap: {
        student: '学生',
        class: '班级',
        grade: '年级',
        school: '学校'
      },
      tags: [],
      loadingTags: false
    }
  },
  mounted () {
    this.userRole = localStorage.getItem('userRole') || 'student'
    this.username = localStorage.getItem('username') || this.userRole
    this.updateTime()
    this.timer = setInterval(this.updateTime, 1000)

    // 如果是学生且处于学生维度，加载标签
    if (this.currentDimension === 'student') {
      this.fetchTags()
    }
  },
  watch: {
    currentDimension (val) {
      if (val === 'student') {
        this.fetchTags()
      }
    }
  },
  beforeDestroy () {
    if (this.timer) {
      clearInterval(this.timer)
    }
  },
  methods: {
    updateTime () {
      const now = new Date()
      this.currentTime = now.toLocaleString()
    },
    toggleConfig () {
      this.isConfigOpen = !this.isConfigOpen
      // 如果打开配置且未选择子项，则选择第一个
      if (this.isConfigOpen && !['userManagement', 'dataImport', 'questionnaireConfig'].includes(this.currentView)) {
        this.currentView = 'userManagement'
      }
    },
    handleLogout () {
      console.log('Logout clicked, showing modal')
      this.showLogoutModal = true
    },
    confirmLogout () {
      this.logLogout(1)
      this.showLogoutModal = false
      // 清除用户信息（如有需要），或直接重定向
      localStorage.removeItem('userRole')
      localStorage.removeItem('username')
      this.$router.push('/')
    },
    cancelLogout () {
      this.logLogout(0)
      this.showLogoutModal = false
    },
    logLogout (status) {
      const username = this.username
      fetch('http://localhost:5000/api/v1/user/logout_log', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: username,
          status: status
        })
      }).catch(err => console.error('Logout logging failed', err))
    },
    getTagClass (tag) {
      if (tag.tag_type === '等级') return 'tag-level'
      return 'tag-quant'
    },
    async fetchTags () {
      const username = this.username
      try {
        const res = await fetch(`http://localhost:5000/api/v1/tags/student?username=${username}`)
        const data = await res.json()
        if (data.success) {
          this.tags = data.data
        } else {
          console.error('Fetch tags failed:', data.msg)
        }
      } catch (err) {
        console.error('Fetch tags error:', err)
      }
    },
    formatValue (val) {
      if (val === null || val === undefined) return ''
      // 尝试转换为数字
      const num = parseFloat(val)
      // 如果不是数字，或者包含非数字字符（如 "优"），返回原值
      if (isNaN(num)) return val

      // 检查原值是否看起来像数字（排除类似 "123a" 这种被 parseFloat 解析的部分）
      // 使用正则检查是否为纯数字或浮点数
      if (!/^-?\d+(\.\d+)?$/.test(String(val))) {
        return val
      }

      // 是数字，保留两位小数
      return num.toFixed(2)
    },
    async generateTags () {
      this.loadingTags = true
      try {
        const res = await fetch('http://localhost:5000/api/v1/tags/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: this.username })
        })
        const data = await res.json()
        if (data.success) {
          alert('标签生成成功')
          this.fetchTags()
        } else {
          alert('生成失败: ' + data.msg)
        }
      } catch (err) {
        alert('生成请求失败')
        console.error(err)
      } finally {
        this.loadingTags = false
      }
    }
  }
}
</script>

<style scoped>
/* 标签样式 */
.generate-btn {
  padding: 4px 8px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.generate-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
.tags-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 43px;
}
.tag-card {
  flex: 0 0 200px;
  background: white;
  border-radius: 8px;
  padding: 12px; /* 稍微减少 padding */
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.tag-header-row {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 10px;
}
.tag-name {
  font-weight: bold;
  color: #333;
}
.info-icon-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-left: 8px;
  cursor: help;
}
.info-icon-wrapper svg {
  vertical-align: middle;
}
.tag-value {
  font-size: 24px;
  color: #2196F3;
  margin: 10px 0;
  font-weight: bold;
}
/* 等级标签样式覆盖 */
.tag-level .tag-value {
  color: #FF9800;
}
</style>

<style scoped>
.home-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: #f0f2f5;
  overflow: hidden;
}

/* 侧边栏样式 */
.sidebar {
  width: 250px;
  background-color: #2b333e;
  color: #fff;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.logo {
  height: 60px;
  line-height: 60px;
  font-size: 18px;
  font-weight: bold;
  padding-left: 20px;
  background-color: #2b333e;
  border-bottom: 1px solid #3f4d67;
}

.nav-menu {
  list-style: none;
  padding: 0;
  margin: 0;
  margin-top: 20px;
  flex: 1; /* 让菜单占据剩余空间，将退出按钮推到底部 */
}

.nav-item {
  height: 50px;
  display: flex;
  align-items: center;
  padding-left: 20px;
  cursor: pointer;
  color: #b8c7ce;
  transition: all 0.3s;
}

.nav-item:hover {
  background-color: #37424f;
  color: #fff;
}

.nav-item.active {
  background-color: #37424f;
  color: #e67e22; /* 橙色高亮文字/图标 */
  border-left: 4px solid #e67e22;
  padding-left: 16px;
}

.nav-item .icon {
  margin-right: 10px;
  width: 20px;
  height: 20px;
  text-align: center;
  display: inline-block;
}

.nav-item .icon svg path {
  fill: currentColor;
}

.nav-item.logout {
  margin-top: auto;
  border-top: 1px solid #3f4d67;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sub-menu {
  list-style: none;
  padding: 0;
  margin: 0;
  background-color: #262c36;
}

.sub-menu-item {
  height: 40px;
  line-height: 40px;
  padding-left: 80px; /* 缩进 */
  color: #7d8085; /* 较暗的灰色 */
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.sub-menu-item:hover {
  color: #fff;
}

.sub-menu-item.active {
  color: #e67e22; /* 橙色高亮 */
}

.header {
  height: 60px;
  background-color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
  flex-shrink: 0;
}

.header-left {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.header-right {
  display: flex;
  align-items: center;
}

.avatar-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #4169e1;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  overflow: hidden;
}

.avatar-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.username {
  font-size: 14px;
  color: #333;
}

.content-wrapper {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  width: 100%;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background-color: transparent;
}

.dashboard-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.dimension-selector {
  display: flex;
  align-items: center;
}

.dimension-label {
  font-size: 14px;
  font-weight: bold;
  margin-right: 10px;
  color: #333;
}

.btn-group {
  display: flex;
  border: 1px solid #4169e1;
  border-radius: 4px;
  overflow: hidden;
}

.dim-btn {
  padding: 6px 16px;
  background-color: #fff;
  border: none;
  border-right: 1px solid #4169e1;
  color: #4169e1;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.dim-btn:last-child {
  border-right: none;
}

.dim-btn.active {
  background-color: #4169e1;
  color: #fff;
}

.dim-btn:hover:not(.active) {
  background-color: #f0f5ff;
}

.container {
  background-color: #fff;
  border-radius: 4px;
  flex: 1; /* 占满剩余高度 */
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  min-height: 400px; /* 最小高度保证 */
  padding: 20px; /* 稍微增加 padding */
  margin: 10px;
  overflow-y: auto;
}

.dimension-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.modal-content {
  background-color: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 400px;
  max-width: 90%;
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 18px;
  color: #333;
}

.modal-content p {
  margin-bottom: 24px;
  color: #666;
  font-size: 14px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.modal-btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  border: none;
  transition: background-color 0.2s;
}

.modal-btn.cancel {
  background-color: #f0f2f5;
  color: #333;
}

.modal-btn.cancel:hover {
  background-color: #e6e8eb;
}

.modal-btn.confirm-logout {
  background-color: #ff4444;
  color: white;
}

.modal-btn.confirm-logout:hover {
  background-color: #cc0000;
}
</style>
