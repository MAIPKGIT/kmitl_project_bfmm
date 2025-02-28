import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  standalone: false,
  styleUrl: './app.component.css'
})
export class AppComponent {
  showNavbar: boolean = true;
  showNavbarKitchen: boolean = false;
  title = 'test-project-app';

  constructor(private router: Router) {
    this.router.events.subscribe(() => {
      const currentUrl = this.router.url;
      this.showNavbar = !['/', '/kitchen-order', '/table'].includes(currentUrl) && !currentUrl.startsWith('/recipe/');
      this.showNavbarKitchen = currentUrl === '/kitchen-order' 
      || currentUrl.startsWith('/recipe/') 
      || currentUrl.startsWith('/ingredient') 
      || currentUrl.startsWith('/waste')
      || currentUrl.startsWith('/history');
    });
  }
}
