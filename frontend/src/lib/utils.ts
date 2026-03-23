import { twMerge, twJoin } from 'tailwind-merge';
import { type ClassValue, clsx } from 'clsx';

/**
 * Merges tailwind classes with clsx
 * @param inputs - Class values to merge
 * @returns Merged tailwind classes
 */
export function cn(...inputs: ClassValue[]) {
	return twMerge(clsx(inputs));
}

/**
 * Joins tailwind classes with clsx
 * @param inputs - Class values to join
 * @returns Joined tailwind classes
 */
export function join(...inputs: ClassValue[]) {
	return twJoin(clsx(inputs));
}
