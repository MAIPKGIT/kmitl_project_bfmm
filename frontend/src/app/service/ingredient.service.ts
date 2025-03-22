import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment.development';

@Injectable({
  providedIn: 'root'
})
export class IngredientService {

  constructor(private http: HttpClient) { }

  getAllPack() {
    let getUrl = `${environment.serviceUrl}/api/ingredientpacks/`;
    return this.http.get<any>(getUrl);
  }

  getAllIngredient() {
    let getUrl = `${environment.serviceUrl}/api/ingredients/`;
    return this.http.get<any>(getUrl);
  }

  createIngredientPack(data: any) {
    let postUrl = `${environment.serviceUrl}/api/ingredientpacks/`;
    return this.http.post<any>(postUrl, data);
  }

  createIngredientPackItem(item: any) {
    let postUrl = `${environment.serviceUrl}/api/ingredientpackitems/`;
    return this.http.post<any>(postUrl, item);
  }

  getPackById(id: number) {
    return this.http.get<any>(`${environment.serviceUrl}/api/ingredientpacks/${id}`);
  }
  
  getItemsByPackId(packId: number) {
    return this.http.get<any>(`${environment.serviceUrl}/api/ingredientpackitems/pack/${packId}`);
  }
  
  updatePack(id: number, data: any) {
    return this.http.put<any>(`${environment.serviceUrl}/api/ingredientpacks/${id}`, data);
  }
  
  updateItem(id: number, data: any) {
    return this.http.put<any>(`${environment.serviceUrl}/api/ingredientpackitems/${id}`, data);
  }
  
  deletePack(id: number) {
    return this.http.delete<any>(`${environment.serviceUrl}/api/ingredientpacks/${id}`);
  }
  
  deleteItem(id: number) {
    return this.http.delete<any>(`${environment.serviceUrl}/api/ingredientpackitems/${id}`);
  }
  
  createIngredient(data: any) {
    return this.http.post<any>(`${environment.serviceUrl}/api/ingredients/`, data);
  }
  
  updateIngredient(id: number, data: any) {
    return this.http.put<any>(`${environment.serviceUrl}/api/ingredients/${id}`, data);
  }
  
  deleteIngredient(id: number) {
    return this.http.delete<any>(`${environment.serviceUrl}/api/ingredients/${id}`);
  }  
}
