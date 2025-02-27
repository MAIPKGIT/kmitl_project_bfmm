import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment.development';

@Injectable({
  providedIn: 'root'
})
export class RecipeService {
  constructor(private http: HttpClient) {}

  getAllMenuTypes() {
    let getUrl = `${environment.serviceUrl}/api/menutype/`;
    return this.http.get<any>(getUrl);
  }

  getAllMenusById(id: any) {
    let getUrl = `${environment.serviceUrl}/api/menu/type/${id}`;
    return this.http.get<any>(getUrl);
  }

  createMenu(menuData: any) {
    let postUrl = `${environment.serviceUrl}/api/menu/`;
    return this.http.post<any>(postUrl, menuData, {
      headers: { 'Content-Type': 'application/json' }
    });
  }

  createStep(stepData: any) {
    let postUrl = `${environment.serviceUrl}/api/step/`;
    return this.http.post<any>(postUrl, stepData);
  }

  getStepById(menu_id: number) {
    let getUrl = `${environment.serviceUrl}/api/step/menu/${menu_id}`;
    return this.http.get<any>(getUrl);
  }

  getMenuById(menu_id: number) {
    let getUrl = `${environment.serviceUrl}/api/menu/${menu_id}`;
    return this.http.get<any>(getUrl);
  }

  updateMenu(menu_id: number, menuData: any) {
    let putUrl = `${environment.serviceUrl}/api/menu/${menu_id}`;
    return this.http.put<any>(putUrl, menuData, {
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  updateStep(stepId: number, stepData: any) {
    let putUrl = `${environment.serviceUrl}/api/step/${stepId}`;
    return this.http.put<any>(putUrl, stepData);
  }

}
