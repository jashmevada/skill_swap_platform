import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'

// PrimeVue Components
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Card from 'primevue/card'
import DataView from 'primevue/dataview'
import Tag from 'primevue/tag'
import Avatar from 'primevue/avatar'
import Dialog from 'primevue/dialog'
import Dropdown from 'primevue/dropdown'
import MultiSelect from 'primevue/multiselect'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import Menubar from 'primevue/menubar'
import Badge from 'primevue/badge'
import Chip from 'primevue/chip'
import Textarea from 'primevue/textarea'
import SelectButton from 'primevue/selectbutton'
import ToggleButton from 'primevue/togglebutton'
import FloatLabel from 'primevue/floatlabel'

// PrimeVue Services
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            prefix: 'p',
            darkModeSelector: '.dark',
            cssLayer: false
        }
    }
})
app.use(ToastService)
app.use(ConfirmationService)

// Global Components
app.component('Button', Button)
app.component('InputText', InputText)
app.component('Password', Password)
app.component('Card', Card)
app.component('DataView', DataView)
app.component('Tag', Tag)
app.component('Avatar', Avatar)
app.component('Dialog', Dialog)
app.component('Dropdown', Dropdown)
app.component('MultiSelect', MultiSelect)
app.component('Toast', Toast)
app.component('ConfirmDialog', ConfirmDialog)
app.component('Menubar', Menubar)
app.component('Badge', Badge)
app.component('Chip', Chip)
app.component('Textarea', Textarea)
app.component('SelectButton', SelectButton)
app.component('ToggleButton', ToggleButton)
app.component('FloatLabel', FloatLabel)

app.mount('#app')
