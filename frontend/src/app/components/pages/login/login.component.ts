import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl } from '@angular/forms';
import Swal from 'sweetalert2';
import { ActivatedRoute, Router } from '@angular/router';
import { LoginService } from '../../../service/login.service';
import { TokenStorageService } from '../../../service/token-storage.service';

@Component({
  selector: 'app-login',
  standalone: false,

  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  loginForm!: FormGroup;
  errMsg = "";
  isLoginFailed = false;
  isLogin = false;
  redirectUrl: string = '/table';

  constructor(private loginService: LoginService, private router: Router, private tokenStorage: TokenStorageService, private route: ActivatedRoute) {
    this.loginForm = new FormGroup({
      username: new FormControl(),
      password: new FormControl()
    });
  }

  ngOnInit(): void {

    if (this.tokenStorage.getToken()) {
      this.isLogin = true;
    }

    this.route.queryParams.subscribe(params => {
      if (params['redirectUrl']) {
        this.redirectUrl = params['redirectUrl']; // ถ้ามี redirectUrl ให้ใช้ path นั้น
      }
    });
  }

  onSubmit(): void {
    const credentials = this.loginForm.value;
    this.loginService.login(credentials).subscribe({
      next: (response: any) => {
        console.log('Test 1 : ',response); 
        this.tokenStorage.saveToken(response.access_token);
        // this.tokenStorage.getToken()
        // console.log('Test 2 : ',this.tokenStorage.getToken());
        this.tokenStorage.saveUser(response.username)
        Swal.fire('Login Successful!', response.message, 'success');
        this.router.navigate([this.redirectUrl]);
      },
      error: (response) => {
        console.error(response.message);
        Swal.fire('Login Failed', response.message, 'error');
      },
    });
  }
}
