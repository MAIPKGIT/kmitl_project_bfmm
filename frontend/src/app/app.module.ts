import { NgModule } from '@angular/core';
import { BrowserModule, provideClientHydration, withEventReplay } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { NavgationComponent } from './components/shared/navgation/navgation.component';
import { ProductComponent } from './components/pages/product/product.component';
import { HttpClientModule , HTTP_INTERCEPTORS  } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { LoginComponent } from './components/pages/login/login.component';
import { OrderingComponent } from './components/ordering/ordering.component';
import { KitchenOrderComponent } from './components/pages/kitchen-order/kitchen-order.component';
import { NavKitchenComponent } from './components/shared/nav-kitchen/nav-kitchen.component';
import { TableStatusComponent } from './components/pages/table-status/table-status.component';
import { AuthInterceptor } from './helper/auth.interceptor';
import { RecipeComponent } from './components/pages/recipe/recipe.component';
import { IngredientComponent } from './components/pages/ingredient/ingredient.component';
import { WasteComponent } from './components/pages/waste/waste.component';

@NgModule({
  declarations: [
    AppComponent,
    NavgationComponent,
    ProductComponent,
    LoginComponent,
    OrderingComponent,
    KitchenOrderComponent,
    NavKitchenComponent,
    TableStatusComponent,
    RecipeComponent,
    IngredientComponent,
    WasteComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule
  ],
  providers: [
    provideClientHydration(withEventReplay()),
    {
      provide: HTTP_INTERCEPTORS, 
      useClass: AuthInterceptor, 
      multi: true // ต้องกำหนดให้เป็น multi
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
