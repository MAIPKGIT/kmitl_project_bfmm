import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { RecipeService } from '../../../service/recipe.service';
import { ViewChild, ElementRef } from '@angular/core';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-recipe',
  standalone: false,
  templateUrl: './recipe.component.html',
  styleUrl: './recipe.component.css'
})
export class RecipeComponent implements OnInit {
  @ViewChild('fileInput') fileInput!: ElementRef;
  menu_types: any[] = [];
  menu_by_type_id: any[] = [];
  category: any;
  selectedId: any;
  newMenu: any = { type_id: '', name: '', des: '', price: null, tag: '', warning: '' };
  selectedFile: File | null = null;
  steps: {
    isNew: boolean;
    id: any; step: number; description: string 
  }[] = [];
  createdMenuId: number | null = null;
  editedMenu: any = {};

  ingredientPacks: any[] = [];
  selectedIngredientPack = { ingredient_pack_id: null, qty: null };
  menuIngredientPacks: any[] = [];

  ingredients: any[] = [];
  menuIngredients: any[] = [];
  selectedMenuIngredient = { ingredient_id: null, volume: null, unit: '' };

  constructor(
    private service: RecipeService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.service.getAllMenuTypes().subscribe((res) => {
      this.menu_types = res;
      console.log('Menu Types:', this.menu_types);
    });

    this.route.params.subscribe(params => {
      this.selectedId = params['id'];
      console.log('Loaded ID from URL:', this.selectedId);

      if (this.selectedId) {
        this.loadMenusById(this.selectedId);
      } else {
        console.error('Category ID is undefined');
      }
    });
  }

  getIngredientPackName(packId: number): string {
    const found = this.ingredientPacks.find(p => p.id === packId);
    return found ? found.name : `ID: ${packId}`;
  }  

  loadIngredientPacks() {
    this.service.getAllIngredientPacks().subscribe(res => {
      this.ingredientPacks = res;
      console.log("Ingredient Packs Loaded:", res);
    });
  }
  
  openIngredientPackModal() {
    const modalEl = document.getElementById('addIngredientPackModal');
    if (!modalEl) {
      console.error("ไม่พบ element modal addIngredientPackModal");
      return;
    }
  
    this.loadIngredientPacks();
  
    const ingredientModal = new (window as any).bootstrap.Modal(modalEl);
    ingredientModal.show();
  }
  
  submitIngredientPack() {
    if (!this.selectedIngredientPack.ingredient_pack_id || !this.selectedIngredientPack.qty) {
      console.log("ไม่มีการเลือก Ingredient Pack — ข้ามไปวัตถุดิบเดี่ยว");
  
      this.selectedIngredientPack = { ingredient_pack_id: null, qty: null };
  
      this.openMenuIngredientModal();
      return;
    }
  
    if (!this.createdMenuId) {
      Swal.fire('Error', 'ไม่พบเมนูที่สร้าง กรุณาลองใหม่', 'error');
      return;
    }
  
    const data = {
      menu_id: this.createdMenuId,
      ingredient_pack_id: this.selectedIngredientPack.ingredient_pack_id,
      qty: this.selectedIngredientPack.qty
    };
  
    this.service.createMenuIngredientPack(data).subscribe(
      res => {
        Swal.fire('Success', 'เพิ่ม Ingredient Pack สำเร็จ!', 'success').then(() => {
          const modalEl = document.getElementById('addIngredientPackModal');
          if (modalEl) {
            const modalInstance = (window as any).bootstrap.Modal.getInstance(modalEl);
            if (modalInstance) modalInstance.hide();
          }
  
          this.selectedIngredientPack = { ingredient_pack_id: null, qty: null };
  
          setTimeout(() => {
            this.openMenuIngredientModal();
          }, 200);
        });
      },
      err => {
        console.error('Error:', err);
        Swal.fire('Error', 'ไม่สามารถเพิ่ม Ingredient Pack ได้', 'error');
      }
    );
  }      

  openMenuIngredientModal() {
    const modalEl = document.getElementById('addMenuIngredientModal');
    if (!modalEl) {
      console.error("ไม่พบ element modal addMenuIngredientModal");
      return;
    }
  
    this.service.getAllIngredients().subscribe(res => {
      console.log("วัตถุดิบทั้งหมด:", res);
      this.ingredients = res;
  
      this.menuIngredients = [{
        id: null,
        menu_id: this.editedMenu.id,
        ingredient_id: null,
        volume: null,
        unit: '',
        isNew: true
      }];
  
      const modal = new (window as any).bootstrap.Modal(modalEl);
      modal.show();
    });
  
    this.selectedMenuIngredient = {
      ingredient_id: null,
      volume: null,
      unit: ''
    };
  }  
  
  async submitMenuIngredient() {
    console.log("submitMenuIngredient called");
    console.log("editedMenu.id:", this.createdMenuId);
    console.log("menuIngredients:", this.menuIngredients);
  
    if (!this.createdMenuId) {
      Swal.fire('Error', 'ไม่พบเมนูที่จะเพิ่มวัตถุดิบ', 'error');
      return;
    }
  
    if (!this.menuIngredients.length) {
      console.log("⏭ไม่มีวัตถุดิบเดี่ยว — ข้ามการเพิ่ม");
      Swal.fire('Success', 'ไม่มีวัตถุดิบเดี่ยวให้เพิ่ม แต่สามารถดำเนินการต่อได้', 'success');
      return;
    }
  
    const hasIncomplete = this.menuIngredients.some(ing =>
      !ing.ingredient_id || !ing.volume || !ing.unit
    );
  
    if (hasIncomplete) {
      Swal.fire('Success', 'ไม่ได้เพิ่มวัตถุดิบเฉพาะ', 'success');
      return;
    }
  
    try {
      for (const ing of this.menuIngredients) {
        const data = {
          menu_id: this.createdMenuId,
          ingredient_id: ing.ingredient_id,
          volume: ing.volume,
          unit: ing.unit
        };
  
        console.log("ส่งข้อมูลวัตถุดิบ:", data);
  
        const res = await this.service.createMenuIngredient(data).toPromise();
        console.log("ส่งสำเร็จ:", res);
      }
  
      Swal.fire('Success', 'เพิ่มวัตถุดิบเดี่ยวสำเร็จ!', 'success');
  
      this.service.getMenuIngredients(this.createdMenuId).subscribe((res) => {
        this.menuIngredients = res.filter((item: any) => item.menu_id === this.createdMenuId);
      });
  
    } catch (error) {
      console.error("Error ส่งวัตถุดิบ:", error);
      Swal.fire('Error', 'ไม่สามารถเพิ่มวัตถุดิบได้บางรายการ', 'error');
    }
  }    

  loadMenusById(id: any) {
    console.log('Fetching menus for category ID:', id);

    this.service.getAllMenusById(id).subscribe(
      (res) => {
        this.menu_by_type_id = res;
        console.log('Menus Loaded:', this.menu_by_type_id);
      },
      (error) => {
        console.error('Error fetching menus:', error);
      }
    );
  }

  getStepByMenuId(menu_id: number) {
    console.log('step: ', menu_id);
  }

  selectMenuTypesById(id: any) {
    let url = `/recipe/${id}`;
    console.log('Navigating to:', url);
    this.router.navigateByUrl('/', { skipLocationChange: true }).then(() => {
      this.router.navigate([url]);
    });
  }

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  createMenu() {
    if (!this.newMenu.type_id || !this.newMenu.name || !this.newMenu.price || !this.selectedFile) {
        Swal.fire('Error', 'กรุณากรอกข้อมูลให้ครบถ้วน', 'error');
        return;
    }

    const menuData = {
        type_id: this.newMenu.type_id,
        name: this.newMenu.name,
        image: this.selectedFile ? this.selectedFile.name : "",
        des: this.newMenu.des ? this.newMenu.des : "",
        price: this.newMenu.price,
        tag: this.newMenu.tag ? this.newMenu.tag : "",
        warning: this.newMenu.warning ? this.newMenu.warning : ""
    };

    console.log("Sending JSON Data:", menuData);

    this.service.createMenu(menuData).subscribe(
        res => {
            console.log("Menu created successfully:", res);
            Swal.fire('Success', 'เพิ่มเมนูสำเร็จ!', 'success');
            this.loadMenusById(this.selectedId);
            this.resetForm();

            setTimeout(() => {
                this.createdMenuId = res.menu_id;
                console.log("🔹 Created menu ID:", this.createdMenuId);

                if (this.createdMenuId) {
                    this.openStepModal();
                } else {
                    console.error("Error: Menu ID is still null.");
                }
            }, 100);
        },
        error => {
            console.error("Error creating menu:", error);
            Swal.fire('Error', 'เกิดข้อผิดพลาด', 'error');
        }
    );
  }

  openStepModal() {
    const stepModalElement = document.getElementById('addStepModal');
    if (!stepModalElement) {
        console.error("Error: Step Modal element not found!");
        return;
    }

    console.log("Opening Step Modal for menu_id:", this.createdMenuId);

    const stepModal = new (window as any).bootstrap.Modal(stepModalElement);
    stepModal.show();
  }


  addStep() {
    const newStep = { id: null, step: this.steps.length + 1, description: "", isNew: true };
    this.steps.push(newStep);
  }

  removeStep(index: number) {
    this.steps.splice(index, 1);
    this.steps.forEach((step, i) => step.step = i + 1);
  }

  async createSteps() {
    if (!this.createdMenuId) {
      console.error("Error: Menu ID is missing.");
      return;
    }
  
    if (this.steps.length === 0) {
      Swal.fire('Warning', 'กรุณาเพิ่มอย่างน้อย 1 ขั้นตอน', 'warning');
      return;
    }
  
    for (const stepData of this.steps) {
      const stepPayload = {
        step: stepData.step,
        menu_id: this.createdMenuId,
        description: stepData.description
      };
  
      console.log(stepPayload);
  
      try {
        const stepRes = await this.service.createStep(stepPayload).toPromise();
        console.log(stepRes);
      } catch (stepErr) {
        console.error('Error creating step:', stepErr);
      }
    }
  
    Swal.fire('Success', 'เพิ่มขั้นตอนสำเร็จ!', 'success').then(() => {
      this.openIngredientPackModal();
    });    
  }  

  async createNewSteps() {
    if (!this.editedMenu.id) {
      console.error("Error: Menu ID is missing.");
      return;
    }
  
    const newSteps = this.steps.filter(step => step.isNew);

    if (newSteps.length === 0) {
      Swal.fire('Warning', 'ไม่มีขั้นตอนใหม่ให้เพิ่ม', 'warning');
      return;
    }

    for (const stepData of newSteps) {
      const stepPayload = {
        step: stepData.step,
        menu_id: this.editedMenu.id, 
        description: stepData.description
      };
  
      console.log(`Creating new step ${stepPayload.step}:`, stepPayload);
  
      try {
        const stepRes = await this.service.createStep(stepPayload).toPromise();
        console.log(`Step ${stepPayload.step} created successfully!`, stepRes);
      } catch (stepErr) {
        console.error('Error creating step:', stepErr);
      }
    }
  
    Swal.fire('Success', 'เพิ่มขั้นตอนใหม่สำเร็จ!', 'success');
  }

  resetForm() {
    this.newMenu = {
        type_id: '',
        name: '',
        des: '',
        price: null,
        tag: '',
        warning: ''
    };
    this.selectedFile = null;
    this.steps = [];
    this.createdMenuId = null;
  }

  onModalClose() {
    this.resetForm();
  }

  trackByFn(index: number, item: any) {
    return item.step;
  }

  getIngredientName(ingredientId: number): string {
    const found = this.ingredients.find(i => i.id === ingredientId);
    return found ? found.name : `ID: ${ingredientId}`;
  }  
  
  openEditMenuModal(menu: any) {
    console.log("เปิด Modal แก้ไขเมนู:", menu);
    
    this.editedMenu = { ...menu }; 
    this.steps = []; 
    this.selectedFile = null;

    if (this.fileInput) {
      this.fileInput.nativeElement.value = "";
    }

    this.loadIngredientPacks();

    this.service.getAllIngredients().subscribe(res => {
      console.log("วัตถุดิบที่โหลดได้", res);
      this.ingredients = res.map((ing: any) => ({
        ingredient_id: ing.Ingredients_id,
        ingredient_name: ing.Ingredients_name
      }));
    });
    
    
    this.service.getMenuIngredients(this.editedMenu.id).subscribe(res => {
      this.menuIngredients = res.filter((item: any) => item.menu_id === this.editedMenu.id);
    });    
  
    this.service.getMenuById(menu.id).subscribe(
      (res) => {
        this.editedMenu = res;
        console.log("ข้อมูลเมนูที่โหลดมา:", this.editedMenu);
      },
      (error) => {
        console.error("Error fetching menu details:", error);
      }
    );

    this.service.getStepById(this.editedMenu.id).subscribe((res) => {
      console.log("Reloading updated steps:", res);
      this.steps = res.map((step: any) => ({
          id: step.id, 
          step: step.step,
          description: step.description,
          isNew: false
      }));
    });

    this.service.getMenuIngredientPacks(this.editedMenu.id).subscribe((res) => {
      this.menuIngredientPacks = res.filter((item: any) => item.menu_id === this.editedMenu.id);
      console.log("Ingredient Packs ในเมนู:", this.menuIngredientPacks);
    });    
  
    const editModal = new (window as any).bootstrap.Modal(document.getElementById('editMenuModal'));
    editModal.show();
  }
  
  updateMenu() {
    if (!this.editedMenu.id) {
      console.error("ไม่มี Menu ID!");
      return;
    }
  
    const updatedData: any = {
      name: this.editedMenu.name,
      des: this.editedMenu.des,
      price: this.editedMenu.price,
      tag: this.editedMenu.tag,
      warning: this.editedMenu.warning
    };

    if (this.selectedFile) {
      updatedData.image = this.selectedFile.name;
    }
  
    console.log("ส่งข้อมูลไปอัปเดตเมนู:", updatedData);
  
    this.service.updateMenu(this.editedMenu.id, updatedData).subscribe(
      (res) => {
        console.log("เมนูอัปเดตสำเร็จ!", res);
        Swal.fire("สำเร็จ", "อัปเดตเมนูเรียบร้อย!", "success");
        
        this.loadMenusById(this.selectedId);
      },
      (error) => {
        console.error("Error updating menu:", error);
        Swal.fire("เกิดข้อผิดพลาด", "ไม่สามารถอัปเดตเมนูได้", "error");
      }
    );
  }
  
  updateSteps(): void {
    if (this.steps.length === 0) {
        Swal.fire('Warning', 'ไม่มีขั้นตอนให้บันทึก', 'warning');
        return;
    }

    this.steps.filter(step => !step.isNew).forEach(step => {
        const stepId = step.id;

        if (!stepId || isNaN(Number(stepId))) {
            console.error("Error: step_id is missing or not a valid number for step:", step);
            return;
        }

        const stepPayload = {
            step: step.step,
            description: step.description,
            menu_id: this.editedMenu.id
        };

        console.log(`Sending update request for Step ID ${stepId}:`, stepPayload);

        this.service.updateStep(stepId, stepPayload).subscribe(
            (res) => {
                console.log(`Step ${stepId} updated successfully`, res);
                this.getStepByMenuId(this.editedMenu.id);
            },
            (error) => {
                console.error(`Error updating step ${stepId}:`, error);
                Swal.fire('Error', 'ไม่สามารถอัพเดทขั้นตอนได้', 'error');
            }
        );
    });

    Swal.fire('Success', 'บันทึกการแก้ไขขั้นตอนสำเร็จ!', 'success');
  }

  updateMenuIngredientPacks() {
    if (this.menuIngredientPacks.length === 0) {
      Swal.fire('Warning', 'ไม่มี Ingredient Pack ที่จะอัปเดต', 'warning');
      return;
    }
  
    for (const pack of this.menuIngredientPacks) {
      const payload = {
        menu_id: pack.menu_id,
        ingredient_pack_id: pack.ingredient_pack_id,
        qty: pack.qty
      };
  
      this.service.updateMenuIngredientPack(pack.id, payload).subscribe(
        (res) => {
          console.log(`อัปเดต Ingredient Pack ID ${pack.id} แล้ว`, res);
        },
        (err) => {
          console.error(`ไม่สามารถอัปเดต Ingredient Pack ID ${pack.id}`, err);
          Swal.fire('Error', 'ไม่สามารถอัปเดต Ingredient Pack ได้', 'error');
        }
      );
    }
  
    Swal.fire('Success', 'อัปเดต Ingredient Pack สำเร็จ!', 'success');
  }  

  addNewMenuIngredient() {
    if (!this.menuIngredients) this.menuIngredients = [];
  
    this.menuIngredients.push({
      id: null,
      menu_id: this.editedMenu.id,
      ingredient_id: null,
      volume: null,
      unit: '',
      isNew: true
    });
  }  

  async createNewMenuIngredients() {
    if (!this.editedMenu.id || !this.menuIngredients.length) {
      Swal.fire('Error', 'ไม่มีข้อมูลวัตถุดิบ', 'error');
      return;
    }
  
    const newIngredients = this.menuIngredients.filter(i => i.isNew);
  
    const hasIncomplete = newIngredients.some(ing =>
      !ing.ingredient_id || !ing.volume || !ing.unit
    );
  
    if (hasIncomplete) {
      Swal.fire('Error', 'กรุณากรอกข้อมูลให้ครบถ้วน', 'error');
      return;
    }
  
    try {
      for (const ing of newIngredients) {
        const data = {
          menu_id: this.editedMenu.id,
          ingredient_id: ing.ingredient_id,
          volume: ing.volume,
          unit: ing.unit
        };
  
        console.log("สร้างวัตถุดิบใหม่:", data);
        const res = await this.service.createMenuIngredient(data).toPromise();
        console.log("สำเร็จ:", res);
      }
  
      Swal.fire('Success', 'เพิ่มวัตถุดิบเดี่ยวใหม่สำเร็จ!', 'success');
  
      this.service.getMenuIngredients(this.editedMenu.id).subscribe((res) => {
        this.menuIngredients = res.filter((item: any) => item.menu_id === this.editedMenu.id);
      });
  
    } catch (error) {
      console.error("เพิ่มวัตถุดิบล้มเหลว:", error);
      Swal.fire('Error', 'ไม่สามารถเพิ่มวัตถุดิบได้บางรายการ', 'error');
    }
  }  
  
  updateMenuIngredients(): void {
    this.menuIngredients = this.menuIngredients.map((item: any) => ({
      ...item,
      id: item.MenuIngredients_id || item.id
    }));
  
    const existingIngredients = this.menuIngredients.filter(ing => !ing.isNew);
  
    if (existingIngredients.length === 0) {
      Swal.fire('Warning', 'ไม่มีวัตถุดิบที่ต้องอัปเดต', 'warning');
      return;
    }
  
    existingIngredients.forEach(ing => {
      const ingredientId = ing.id;
  
      if (!ingredientId || isNaN(Number(ingredientId))) {
        console.error("ไม่มี ID หรือ ID ไม่ถูกต้อง:", ing);
        return;
      }
  
      if (!ing.ingredient_id || !ing.volume || !ing.unit) {
        console.warn("พบข้อมูลไม่ครบ:", ing);
        return;
      }
  
      const payload = {
        menu_id: this.editedMenu.id,
        ingredient_id: ing.ingredient_id,
        volume: ing.volume,
        unit: ing.unit
      };
  
      console.log(`ส่งอัปเดตวัตถุดิบเดี่ยว ID ${ingredientId}:`, payload);
  
      this.service.updateMenuIngredient(ingredientId, payload).subscribe(
        (res) => {
          console.log(`วัตถุดิบ ID ${ingredientId} อัปเดตสำเร็จ`, res);
          this.service.getMenuIngredients(this.editedMenu.id).subscribe((res) => {
            this.menuIngredients = res.filter((item: any) => item.menu_id === this.editedMenu.id)
              .map((item: any) => ({
                ...item,
                id: item.MenuIngredients_id || item.id
              }));
          });
        },
        (err) => {
          console.error(`อัปเดตวัตถุดิบ ID ${ingredientId} ล้มเหลว`, err);
          Swal.fire('Error', `ไม่สามารถอัปเดตวัตถุดิบ ID ${ingredientId} ได้`, 'error');
        }
      );
    });
  
    Swal.fire('Success', 'บันทึกการแก้ไขวัตถุดิบเดี่ยวสำเร็จ!', 'success');
  }    
  
  deleteMenuIngredient(id: number) {
    if (!id) {
      this.menuIngredients = this.menuIngredients.filter(i => !i.isNew || i.id !== id);
      return;
    }
  
    this.service.deleteMenuIngredient(id).subscribe(
      res => {
        this.menuIngredients = this.menuIngredients.filter(i => i.id !== id);
        Swal.fire('Deleted', 'ลบวัตถุดิบเดี่ยวแล้ว', 'success');
      },
      err => Swal.fire('Error', 'ลบไม่สำเร็จ', 'error')
    );
  }  

  deleteFullMenu(): void {
    if (!this.editedMenu.id) {
      console.error("ไม่พบ ID เมนู");
      Swal.fire("Error", "ไม่พบ ID เมนู", "error");
      return;
    }
  
    Swal.fire({
      title: "ยืนยันการลบเมนูนี้?",
      text: "การลบนี้จะลบข้อมูลทั้งหมดที่เกี่ยวข้องกับเมนูนี้ด้วย",
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "ใช่, ลบเลย",
      cancelButtonText: "ยกเลิก"
    }).then(async (result) => {
      if (!result.isConfirmed) return;
  
      const menuId = this.editedMenu.id;
  
      try {
        if (this.steps.length > 0) {
          for (const step of this.steps) {
            if (step.id) {
              await this.service.deleteStep(step.id).toPromise();
              console.log(`ลบ Step ID ${step.id} สำเร็จ`);
            }
          }
        }
        if (this.menuIngredientPacks.length > 0) {
          for (const pack of this.menuIngredientPacks) {
            if (pack.id) {
              await this.service.deleteMenuIngredientPack(pack.id).toPromise();
              console.log(`ลบ Ingredient Pack ID ${pack.id} สำเร็จ`);
            }
          }
        }
        if (this.menuIngredients.length > 0) {
          for (const ing of this.menuIngredients) {
            if (ing.MenuIngredients_id) {
              await this.service.deleteMenuIngredient(ing.MenuIngredients_id).toPromise();
              console.log(`ลบวัตถุดิบ ID ${ing.MenuIngredients_id} สำเร็จ`);
            }
          }
        }
        await this.service.deleteMenu(menuId).toPromise();
        console.log(`ลบเมนูหลัก ID ${menuId} สำเร็จ`);
  
        Swal.fire("Deleted!", "ลบเมนูและข้อมูลที่เกี่ยวข้องแล้ว", "success");
        this.loadMenusById(this.selectedId);
  
        const editModal = (window as any).bootstrap.Modal.getInstance(document.getElementById('editMenuModal'));
        if (editModal) editModal.hide();
        this.editedMenu = {};
        this.steps = [];
        this.menuIngredientPacks = [];
        this.menuIngredients = [];
      } catch (err) {
        console.error("ลบเมนูไม่สำเร็จ:", err);
        Swal.fire("Error", "เกิดข้อผิดพลาดระหว่างลบเมนู", "error");
      }
    });
  }  
}