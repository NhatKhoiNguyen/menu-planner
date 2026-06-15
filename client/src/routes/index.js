import Home from '~/pages/Home/Home';
import MealHistory from '~/pages/MealHistory/MealHistory';
import FavoriteMeals from '~/pages/FavoriteMeals/FavoriteMeals';
import AdminDashboard from '~/pages/AdminDashboard/AdminDashboard';
import UserContribution from '~/pages/UserContribution/UserContribution';
import ResetPassword from '~/pages/ResetPassword/ResetPassword';
import UserProfile from '~/pages/UserProfile/UserProfile';
import Search from '~/pages/Search/Search';

const publicRoutes = [
    { path: '/', component: Home },
    { path: '/history', component: MealHistory },
    { path: '/favorites', component: FavoriteMeals },
    { path: '/contribution', component: UserContribution },
    { path: '/profile', component: UserProfile },
    { path: '/reset-password/:token', component: ResetPassword },
    { path: '/search', component: Search},

]

const privateRoutes = [
    { path: '/admin', component: AdminDashboard, roles: ['admin'] },
]

export { publicRoutes, privateRoutes }